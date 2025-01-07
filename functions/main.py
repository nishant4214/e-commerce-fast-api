from fastapi import FastAPI, HTTPException, APIRouter
from supabase import create_client, Client
from pydantic import BaseModel, Field
from mangum import Mangum

SUPABASE_URL = "https://wplynhlsjjzczsgembup.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwbHluaGxzamp6Y3pzZ2VtYnVwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyOTUwNzM5MSwiZXhwIjoyMDQ1MDgzMzkxfQ.UOg9HpjHXLIP7s__uKsNI6XJ0_seUQBGK7UhD8nzgZk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = FastAPI()

@app.get("/AllProducts")
async def get_products():
    try:
        response = supabase.table("products").select("*").execute()
        products = response.data
        if not products:
            raise HTTPException(status_code=404, detail="No products found")

        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProductRequest(BaseModel):
    product_id: int

@app.post("/GetProductById")
async def get_product_by_id(request: ProductRequest):
    try:
        response = supabase.table("products").select("*").eq("id", request.product_id).execute()
        
        product = response.data
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return {"product": product}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AddProductRequest(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the product")
    price: float = Field(..., gt=0, description="Price of the product")
    description: str = Field(None, description="Description of the product")
    image_url: str = Field(None, description="URL of the product image")
    category_id: int = Field(..., description="ID of the category the product belongs to")

@app.post("/AddProduct")
async def add_product(request: AddProductRequest):
    try:
        response = supabase.table("products").select("*").eq("name", request.name).execute()

        if response.data and len(response.data) > 0:
            raise HTTPException(status_code=400, detail="A product with the same name already exists.")

        response = supabase.table("products").insert({
            "name": request.name,
            "price": request.price,
            "description": request.description,
            "image_url": request.image_url,
            "category_id": request.category_id,
        }).execute()

        return {"message": "Product added successfully", "product": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class UpdateProductRequest(BaseModel):
    product_id: int
    name: str = None
    price: float = None
    description: str = None
    image_url: str = None
    category_id: int = None

@app.put("/UpdateProduct")
async def update_product(request: UpdateProductRequest):
    try:
        response = supabase.table("products").select("*").eq("name", request.name).execute()

        if response.data and len(response.data) > 0:
            raise HTTPException(status_code=400, detail="A product with the same name already exists.")

        # Check if the product exists
        product_response = supabase.table("products").select("*").eq("id", request.product_id).execute()
        if not product_response.data or len(product_response.data) == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        # Prepare fields to update dynamically
        update_fields = {}
        if request.name:
            update_fields["name"] = request.name
        if request.price:
            update_fields["price"] = request.price
        if request.description:
            update_fields["description"] = request.description
        if request.image_url:
            update_fields["image_url"] = request.image_url
        if request.category_id:
            update_fields["category_id"] = request.category_id

        # Perform the update
        update_response = supabase.table("products").update(update_fields).eq("id", request.product_id).execute()
        return {
            "message": "Product updated successfully",
            "product": update_response.data
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = Mangum(app)
