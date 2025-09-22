from fastapi import FastAPI,Request
from routers import get_db_api,json_api,post_db_api,post_db_api
import time
import time
from logger_setup.all_logger import logger 
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback



app = FastAPI()
  


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as exp:
        print("error occured sorry")
        log_str = traceback.format_exc()
        logger.critical(f"{exp}, {log_str}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "server side error"})
    else:
        process_time = time.time() - start_time
        logger.info(
            f"Completed {request.method} {request.url.path} "
            f"Status {response.status_code} in {process_time:.4f}s"
        )
        return response

    


app.include_router(get_db_api.router)
app.include_router(json_api.json_router_)
app.include_router(post_db_api.router_put_db)
app.include_router(post_db_api.router_put_db)


