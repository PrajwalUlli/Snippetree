
from .create_logger import setup_logging  

def divide(a, enable_log=False):  
    # Setup logging based on the parameter
    # You can also leave the file_path and it will create files based on which file called the logger import
    log = setup_logging(enable_log=enable_log, log_file_path="app.log")  
      
    log.info("Application started")
            
    try:          
        result = 1 / 0          
    except ZeroDivisionError:          
        log.error("Division by zero error", exc_info=True)  
      
divide(2, True)
