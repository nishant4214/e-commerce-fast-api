# FastAPI Product Management API

This repository contains a FastAPI-based backend API for managing products and categories. The API connects to a Supabase database and provides endpoints for CRUD operations on products and categories.

---

## Features

1. Fetch all products with categories.
2. Fetch all product categories.
3. Fetch product details by ID.
4. Fetch products by category ID.
5. Search products by name.
6. Add a new product.
7. Update existing product details.
8. Soft delete a product.

---

## Technologies Used

- **FastAPI**: Web framework for building APIs.
- **Supabase**: Backend-as-a-Service (BaaS) for database management.
- **Pydantic**: Data validation and settings management.
- **Python**: Programming language.

---

## Installation and Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nishant4214/e-commerce-fast-api.git
   cd your-repo-name
   ```

2. **Set up a Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate # For Linux/MacOS
   venv\Scripts\activate   # For Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install python-multipart
   pip install os
   pip install -r requirements.txt
   ```

4. **Set environment variables**:
   Create a `.env` file in the root directory with the following content:
   ```env
   SUPABASE_URL=<Your-Supabase-URL>
   SUPABASE_ANON_KEY=<Your-Supabase-ANON-KEY>
   ```

5. **Run the server**:
   ```bash
   uvicorn minio_app:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Access the API documentation**:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Environment Variables

- `SUPABASE_URL`: Your Supabase project URL.
- `SUPABASE_ANON_KEY`: Your Supabase anonymous API key.

---

## Endpoints

### **Products**

1. **Get All Products**
   - **URL**: `/AllProducts`
   - **Method**: `GET`

2. **Get Product By ID**
   - **URL**: `/GetProductById`
   - **Method**: `GET`
   - **Query Parameters**:
     - `product_id` (int): The ID of the product.

3. **Get Products By Category ID**
   - **URL**: `/GetProductByCategoryId`
   - **Method**: `GET`
   - **Query Parameters**:
     - `category_id` (int): The ID of the category.

4. **Search Products By Name**
   - **URL**: `/SearchProductByName`
   - **Method**: `GET`
   - **Query Parameters**:
     - `product_name` (str): The name or partial name of the product.

5. **Add Product**
   - **URL**: `/AddProduct`
   - **Method**: `POST`
   - **Request Body**:
     ```json
     {
       "name": "Product Name",
       "price": 100.0,
       "description": "Product description",
       "image_url": "http://example.com/image.jpg",
       "category_id": 1
     }
     ```

6. **Update Product**
   - **URL**: `/UpdateProduct`
   - **Method**: `PUT`
   - **Request Body**:
     ```json
     {
       "product_id": 1,
       "name": "Updated Name",
       "price": 150.0,
       "description": "Updated description",
       "image_url": "http://example.com/updated-image.jpg",
       "category_id": 2
     }
     ```

7. **Delete Product By ID**
   - **URL**: `/DeleteProductById`
   - **Method**: `DELETE`
   - **Request Body**:
     ```json
     {
       "product_id": 1
     }
     ```

### **Categories**

1. **Get All Categories**
   - **URL**: `/AllProductCategories`
   - **Method**: `GET`

---

## Deployment

### **To Deploy on Render**

1. **Create a new Web Service** on [Render](https://render.com).
2. Link your GitHub repository.
3. Set the following environment variables in the Render dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
4. Set the build and start commands:
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000
     ```
5. Deploy the service.

---

## Contributing

1. Fork the repository.
2. Create a new branch (`feature/your-feature`).
3. Commit your changes.
4. Push to the branch.
5. Open a pull request.

---
