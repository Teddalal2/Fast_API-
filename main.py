from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from database import get_db, engine
import database_models


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],  # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # allow headers like Content-Type, Authorization
)

# Create tables
database_models.Base.metadata.create_all(bind=engine)


@app.get("/")
def greet():
    return "Welcome to the Python programming world!"


# Dummy in-memory products (optional)
products = [
    Product(
        id=1,
        name="Laptop",
        description="A high-performance laptop",
        price=999.99,
        quantity=10,
    ),
    Product(
        id=2,
        name="Mouse",
        description="Wireless optical mouse",
        price=29.99,
        quantity=50,
    ),
    Product(
        id=3,
        name="Keyboard",
        description="Mechanical keyboard",
        price=79.99,
        quantity=30,
    ),
    Product(
        id=4,
        name="Monitor",
        description="24-inch LED monitor",
        price=199.99,
        quantity=20,
    ),
]


# Initialize DB (Insert sample data)
def init_db(db: Session):

    count = db.query(database_models.Product).count()

    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))

        db.commit()


# Run once at startup
@app.on_event("startup")
def startup_event():

    db = next(get_db())  # get real DB session

    try:
        init_db(db)
    finally:
        db.close()


@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()


@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = (
        db.query(database_models.Product)
        .filter(database_models.Product.id == id)
        .first()
    )

    if not product:
        return {"error": "Product not found"}

    return product


@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):

    data = product.model_dump(exclude={"id"})  # remove id

    db_product = database_models.Product(**data)

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = (
        db.query(database_models.Product)
        .filter(database_models.Product.id == id)
        .first()
    )

    if not db_product:
        return {"error": "Product not found"}

    for key, value in product.model_dump().items():
        setattr(db_product, key, value)

    db.commit()
    return db_product


@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = (
        db.query(database_models.Product)
        .filter(database_models.Product.id == id)
        .first()
    )

    if not db_product:
        return {"error": "Product not found"}

    db.delete(db_product)
    db.commit()

    return {"message": "Product deleted successfully"}
