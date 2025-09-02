from internal.connector import getSupabase
from internal.templates import Messages
from internal.logger import logger 

## [TODO] Add Method for compression of image
async def ImageUploader(local_path, remote_path):
    try:
        supabase = getSupabase()
        # find a method to check if image already exists, if it does 
        # replace/delete the image and add new image
        # step 1: find if the image already exists 
        images = supabase.storage.from_("item-images").list()
        names = [item['name'] for item in images]
        if remote_path in names:
            print("Control is going here?")
            with open(local_path, "rb") as f:
                supabase.storage.from_("item-images").update(
                    file=f,
                    path=remote_path,
                    file_options={"cache-control": "3600", "upsert": "true"}
                )
        else: 
            with open(local_path, "rb") as f:
                supabase.storage.from_("item-images").upload(
                    file=f,
                    path=remote_path,
                    file_options={"cache-control": "3600", "upsert": "false"}
                )
        return Messages.success(message="Image successfully uploaded")
        
    except Exception as e:
        logger.error(f"Error Origin: internal/utilities.py \nException has occurred: {e}")
        return Messages.exception_message(origin="internal/utilities.py",message="Error Uploading Image",exception=e)