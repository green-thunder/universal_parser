from fastapi import FastAPI, File, UploadFile
from get_link import GatherLinks
from get_data import GatherData
import uvicorn
import pandas as pd

import json

app = FastAPI()

linkpath = 'datasets/weblinks.csv'
jsonlinkpath = 'datasets/links.json'
verify = False

@app.post("/files")
async def upload_file(file: UploadFile = File(...)):
    try:
        with open(linkpath, 'wb') as f:
            f.write(file.file.read())
            verify = True
    except Exception:
        verify = False

    if verify:
        return "File muofiqiyatli saqlandi."
    else:
        return "File saqlanmadi."

@app.post("/files/links/{start}")
async def create_links(start: bool):

    if start:
        df = pd.read_csv(linkpath)
        websites = df.to_dict(orient='records')

        gather = GatherLinks(jsonlinkpath)
        gather.collect(websites)
        gather.save()
        return {'message': "Links muvaffaqiyatli saqlandi."}  
   
        
@app.post("/files/data/{start}/{text}/{img}")
async def gather_data(start: bool, text:bool, img:bool):
      
        with open(jsonlinkpath, 'r') as f:
            url_hub = json.load(f)
        try:
           
           if start:
                
                gather_data = GatherData(url_hub)
                gather_data.perform_operations(parse_text=text, parse_images=img, save_text=text, save_images=img)


                return {'message': "Data samarali saqlandi."}
           else:
                
                return {'message': "Data scrape qilishga ruxsat berilmagan."}
        except Exception as e:
             
            return {'message': f"Xatolik yuzberdi.: {str(e)}."}
        
if __name__ == "__main__":

      uvicorn.run("run:app", host="127.0.0.1", port=8000)
