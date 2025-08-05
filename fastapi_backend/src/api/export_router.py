from fastapi import APIRouter, Depends, HTTPException
import services.export_service as service
from sqlalchemy.orm import Session
from db.database import get_db

from fastapi.responses import StreamingResponse
import io
import json

router = APIRouter(prefix="/digital-twins/{digital_twin_id}/export", tags=["Digital Twin Export"])

@router.get("/download.json")
async def export_digital_twin_file(digital_twin_id: int, db: Session = Depends(get_db)):
    try:
        name, export_data = service.export_digital_twin(db, digital_twin_id)
        file_like = io.BytesIO(json.dumps(export_data, indent=2).encode("utf-8"))

        return StreamingResponse(file_like, media_type="application/json", headers={
            "Content-Disposition": f"attachment; filename={name}.config.json"
        })
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Export error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")