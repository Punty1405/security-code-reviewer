"""
FastAPI service for security code review
"""

import tempfile
import time
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from src.graph import app as agent_app
from src.config import LANGCHAIN_PROJECT

# Response models
class Finding(BaseModel):
    """
    Base finding model
    """
    pass

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict

class SuccessResponse(BaseModel):
    success: bool = True
    findings: dict
    markdown_comment: str
    metadata: dict

# FastAPI App
app = FastAPI(
    title='Security Code Reviewer',
    description='LLM-powered security review for Python PRs (CWE-89, CWE-78, CWE-22)',
    version='1.0.0'
)

@app.post('/review')
async def review_code(
    file: UploadFile = File(..., description='ZIP file containing codebase'), 
    diff_text: str = Form(..., description='PR diff in unified format')) -> JSONResponse:
    """
    Review code for security vulnerabilities
    
    Accepts:
    - ZIP file with Python codebase
    - PR diff text (unified diff format)
    
    Returns:
    - Validated Bandit findings
    - Rejected Bandit findings
    - Semantic-only findings
    - Markdown PR comment
    - Execution metadata
    """

    start_time = time.time()
    temp_zip = None

    try:
        # Check for correct inputs
        if not file.filename.endswith('.zip'):
            raise HTTPException(
                status_code=400,
                detail={
                    'type': 'InvalidZIP',
                    'message': 'File must be a ZIP archive',
                    'details': f"Recieved: {file.filename}"
                }
            )

        if not diff_text or not diff_text.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    'type': 'InvalidDiff',
                    'message': 'diff_text cannot be empty',
                    'details': 'Provide PR diff in unified format'
                }
            )
        
        # Normalize diff text - swaggerUI mangling newlines
        # Replace literal \n strings with actual newlines
        diff_text = diff_text.replace('\\n', '\n')

        # If still no newlines, try to reconstruct from patterns
        if '\n' not in diff_text:
            # Add newlines before diff markers
            import re
            diff_text = re.sub(r'(diff --git)', r'\n\1', diff_text)
            diff_text = re.sub(r'(---)', r'\n\1', diff_text)  
            diff_text = re.sub(r'(\+\+\+)', r'\n\1', diff_text)
            diff_text = re.sub(r'(@@)', r'\n\1', diff_text)
            diff_text = diff_text.strip()
        
        # Uploaded zip file in temp
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_zip = tmp.name


        # Check if ZIP file can be opened
        import zipfile
        try:
            with zipfile.ZipFile(temp_zip, 'r') as z:
                # Does it have python files?
                py_files = [f for f in z.namelist() if f.endswith('.py')]
                if not py_files:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            'type': 'NoPythonFiles',
                            'message': 'No Python files found in ZIP',
                            'details': f'Files in ZIP: {len(z.namelist())}'
                        }
                    )

        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=400,
                detail={
                    'type': 'InvalidZIP',
                    'message': 'File is not valid ZIP archive',
                    'details': 'Could not open ZIP file'
                }
            )
        
        # Run the agent now
        try:
            result = agent_app.invoke({
                'zip_path': temp_zip,
                'diff_text': diff_text
            })

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail = {
                    'type': 'ExecutionError',
                    'message': 'Agent execution Failed',
                    'details': str(e)
                }
            )

        execution_time = time.time() - start_time

        # Building LangSmith Trace if available
        if os.getenv('LANGCHAIN_TRACING_V2')=='true':
            # No run-id generated during execution - no additional metadata added.
            # So, just link to the project and allow them to navigate
            trace_url = f"https://smith.langchain.com/o/default/projects/p/{LANGCHAIN_PROJECT}"

        response = {
            "success": True,
            "findings": result.get("final_json", {}),
            "markdown_comment": result.get("final_markdown", "")
            }

        return JSONResponse(content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                'type': 'ExecutionError',
                'message': 'Unexpected error during processing',
                'details': str(e)
            }
        )
    
    finally:
        # Clean up the tmp
        if temp_zip and os.path.exists(temp_zip):
            os.unlink(temp_zip)


@app.get('/health')
async def health_check():
    """
    Health checkpoint
    """
    return {'status': 'Healthy', 'service': 'security-code-reviewer'}

@app.get("/")
async def root():
    """Redirect to docs"""
    return RedirectResponse(url="/docs")