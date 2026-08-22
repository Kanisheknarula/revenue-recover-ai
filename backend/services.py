from backend.data import customers_data

def find_customer(customer_id: str):
    for customer in customers_data:
        if customer["customer_id"] == customer_id:
            return customer
    return None
