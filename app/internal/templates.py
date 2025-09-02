from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
# Templating for multiple classes
 
class Messages:
    @staticmethod
    def exception_message(origin: str, message: str, exception: Exception, status_code: int = 500):
        return JSONResponse(
            {
                "origin": origin,
                "message": message,
                "exception": str(exception),  # ✅ convert to string
            },
            status_code=status_code
        )
    
    def user_error(message,status_code=404):
        return JSONResponse(
            {
                "message":message,
            },
            status_code=status_code
        )

    def success(message):
        return JSONResponse(
            {   
                "message": message,
            },
            status_code=200
        )
    
    def message(content,headers):
        return JSONResponse(
                content=jsonable_encoder(content),
                headers=headers,
                status_code=200 
        )