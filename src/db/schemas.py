import datetime

from pydantic import BaseModel, UUID4


class GetProducts(BaseModel):
	id: UUID4
	name: str
	vendor_code: str
	price: int
	rating: float
	qty: int


class Request(BaseModel):
	id: UUID4
	user_id: int
	date_request: datetime.datetime
	vendor_code: str


class GetProductsFromDB(BaseModel):
	name: str
	vendor_code: str
	price: int
	rating: float
	qty: int
