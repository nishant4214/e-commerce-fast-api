from fastapi import FastAPI, HTTPException,Query, Depends,status
from supabase import create_client, Client
from pydantic import BaseModel, Field, field_validator
import re
import os
from dotenv import load_dotenv
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=10)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    mobile_no: Union[str, None] = None

class User(BaseModel):
    id: int
    mobile_no: str
    full_name: Union[str, None] = None
    isactive: bool

class UserInDB(User):
    password: str

def verify_password(plain_password, hashed_password):

    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(mobile_no: str):
    """Fetch user from Supabase users table"""

    response = supabase.table("users").select("id,mobile_no,full_name,password,isactive").eq("mobile_no", mobile_no).execute()


    if response.data and len(response.data) > 0:
        user_data = response.data[0]
        return UserInDB(
            id=user_data["id"],
            mobile_no=user_data["mobile_no"],
            full_name=user_data["full_name"],
            password=user_data["password"],  # Hashed password
            isactive=user_data["isactive"],

        )

    print("User not found.")
    return None

async def authenticate_user(mobile_no: str, password: str):
    """Authenticate user by verifying password"""
    user = await get_user(mobile_no)
    if not user or not verify_password(password, user.password):  
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Retrieve current authenticated user"""
   
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mobile_no: str = payload.get("sub")
        if mobile_no is None:
            raise credentials_exception
        user = await get_user(mobile_no)
        if user is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.isactive:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile no or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.mobile_no})
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

class AddProductRequest(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the product")
    price: float = Field(..., gt=0, description="Price of the product")
    description: str = Field(None, max_length=500,  description="Description of the product")
    image_url: str = Field(None, description="URL of the product image")
    category_id: int = Field(..., gt=0, description="ID of the category the product belongs to")

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
class DeleteProductById(BaseModel):
    product_id: int

    @field_validator("product_id")
    def validate_category_id(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Product ID must be a positive integer.")
        return value

@app.get("/AllProducts", dependencies=[Depends(get_current_user)])
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

@app.get("/AllProductCategories", dependencies=[Depends(get_current_user)])
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
    except InvalidTokenError:
        raise credentials_exception

@app.get("/GetProductById", dependencies=[Depends(get_current_user)])
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
    except InvalidTokenError:
        raise credentials_exception


@app.get("/GetProductByCategoryId", dependencies=[Depends(get_current_user)])
async def get_product_by_category_id(    
    category_id: int = Query(..., gt=0, description="The positive integer ID of the category to fetch products")
):
    """
    Fetch a product by its category ID.
    """
    try:
        response = supabase.table("products").select("id, name, description, price, isactive, category_id").eq("category_id", category_id).eq("isactive", True).execute()

        product = response.data
        if not product:
            raise HTTPException(status_code=404, detail="Products not found for given category id")

        return product
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except InvalidTokenError:
        raise credentials_exception

@app.get("/SearchProductByName", dependencies=[Depends(get_current_user)])
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
    except InvalidTokenError:
        raise credentials_exception
 

@app.post("/AddProduct", dependencies=[Depends(get_current_user)])
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
    except InvalidTokenError:
        raise credentials_exception
   

@app.put("/UpdateProduct", dependencies=[Depends(get_current_user)])
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
    except InvalidTokenError:
        raise credentials_exception


@app.delete("/DeleteProductById", dependencies=[Depends(get_current_user)])
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
    except InvalidTokenError:
        raise credentials_exception