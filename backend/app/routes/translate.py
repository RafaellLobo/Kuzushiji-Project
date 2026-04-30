from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.services.errors import PipelineError

router = APIRouter(prefix="/translate", tags=["translate"])


@router.post("")
async def translate(request: Request, image: UploadFile = File(...)):
    image_bytes = await image.read()

    try:
        return await request.app.state.translation_pipeline.process(
            image_bytes=image_bytes,
            content_type=image.content_type,
        )
    except PipelineError as exc:
        if exc.status_code >= 400:
            raise HTTPException(status_code=exc.status_code, detail=exc.to_response()) from exc
        return exc.to_response()
