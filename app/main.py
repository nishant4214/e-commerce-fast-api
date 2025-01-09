from fastapi import FastAPI, HTTPException,Query
from supabase import create_client, Client
from pydantic import BaseModel, Field, field_validator
import re
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = FastAPI()

@app.get("/AllProducts")
async def get_products():
    try:
        response = supabase.table("products").select("id, name, description, price, isactive, categories(category_id, category_name)").eq("isactive", True).execute()
        products = response.data
        if not products:
            raise HTTPException(status_code=404, detail="No products found")

        return products
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/AllProductCategories")
async def get_all_product_categories():
    try:
        response = supabase.table("categories").select("category_id, category_name, is_prescription_required, is_otc, is_medicine, is_medical_device").execute()
        categories = response.data
        if not categories:
            raise HTTPException(status_code=404, detail="No category found")

        return categories
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/GetProductById")
async def get_product_by_id(    
    product_id: int = Query(..., gt=0, description="The positive integer ID of the product to fetch")
):
    """
    Fetch a product by its ID.
    """
    try:
        response = supabase.table("products").select("id, name, description, price, image_url, isactive, categories(category_id, category_name)").eq("id", product_id).eq("isactive", True).execute()

        product = response.data
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GetProductByCategoryId")
async def get_product_by_category_id(    
    category_id: int = Query(..., gt=0, description="The positive integer ID of the category to fetch products")
):
    """
    Fetch a product by its category ID.
    """
    try:
        response = supabase.table("categories").select("products(id, name, description, price, isactive, category_id)").eq("category_id", category_id).execute()

        product = response.data
        if not product:
            raise HTTPException(status_code=404, detail="Products not found for given category id")

        return product
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/SearchProductByName")
async def search_product_by_name(    
    product_name: str = Query(...,max_length=100,  description="The string of the product name to fetch")
):

    """
    Filter products by Name.
    """
    try:
        if not re.match(r"^[a-zA-Z0-9\s]+$", product_name):
            raise HTTPException(status_code=400, detail="Product name should not contain special characters.")
    
        response = supabase.table("products").select("id, name, description, price, isactive, categories(category_id, category_name)").ilike("name", f"%{product_name}%").execute()

        products = response.data
        if not products:
            raise HTTPException(status_code=404, detail="No products found matching the given name.")

        return products
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class AddProductRequest(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the product")
    price: float = Field(..., gt=0, description="Price of the product")
    description: str = Field(None, description="Description of the product")
    image_url: str = Field(None, description="URL of the product image")
    category_id: int = Field(..., description="ID of the category the product belongs to")

    @field_validator("name")
    def validate_name(cls, value): 
        if not re.match(r"^[a-zA-Z0-9\s]+$", value):
            raise ValueError("Name should not contain special characters.")
        return value

    @field_validator("description")
    def validate_description(cls, value):
        if value and not re.match(r"^[a-zA-Z0-9\s,.!?-]*$", value):
            raise ValueError("Description should not contain special characters.")
        return value

    @field_validator("price")
    def validate_price(cls, value):
        if not isinstance(value, float):
            raise ValueError("Price must be a float.")
        return value

    @field_validator("category_id")
    def validate_category_id(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Category ID must be a positive integer.")
        return value

@app.post("/AddProduct")
async def add_product(request: AddProductRequest):
    try:
        response = supabase.table("products").select("name").eq("name", request.name).execute()

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
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class UpdateProductRequest(BaseModel):
    product_id: int
    name: str = None
    price: float = None
    description: str = None
    image_url: str = None
    category_id: int = None

    @field_validator("product_id")
    def validate_category_id(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Product ID must be a positive integer.")
        return value
    
    @field_validator("name")
    def validate_name(cls, value): 
        if not re.match(r"^[a-zA-Z0-9\s]+$", value):
            raise ValueError("Name should not contain special characters.")
        return value

    @field_validator("description")
    def validate_description(cls, value):
        if value and not re.match(r"^[a-zA-Z0-9\s,.!?-]*$", value):
            raise ValueError("Description should not contain special characters.")
        return value

    @field_validator("price")
    def validate_price(cls, value):
        if not isinstance(value, float):
            raise ValueError("Price must be a float.")
        return value

    @field_validator("category_id")
    def validate_category_id(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Category ID must be a positive integer.")
        return value

@app.put("/UpdateProduct")
async def update_product(request: UpdateProductRequest):
    try:
        response = supabase.table("products").select("id, name").eq("name", request.name).neq("id", request.product_id).execute()

        if response.data and len(response.data) > 0:
            raise HTTPException(status_code=400, detail="A product with the same name already exists.")

        product_response = supabase.table("products").select("*").eq("id", request.product_id).execute()
        if not product_response.data or len(product_response.data) == 0:
            raise HTTPException(status_code=404, detail="Product not found")

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

        update_response = supabase.table("products").update(update_fields).eq("id", request.product_id).execute()
        return {
            "message": "Product updated successfully",
            "product": update_response.data
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DeleteProductById(BaseModel):
    product_id: int

    @field_validator("product_id")
    def validate_category_id(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Product ID must be a positive integer.")
        return value

@app.delete("/DeleteProductById")
async def delete_product_by_id(request: DeleteProductById):
    try:
        product_response = supabase.table("products").select("id").eq("id", request.product_id).execute()
        if not product_response.data or len(product_response.data) == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        update_response = supabase.table("products").update({"isactive": False}).eq("id", request.product_id).execute()

        return {
            "message": "Product deleted successfully",
            "product": update_response.data
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

