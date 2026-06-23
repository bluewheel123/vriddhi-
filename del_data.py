from pymongo import MongoClient

def run_mongodb_demo():
    try:
        client = MongoClient("mongodb+srv://sunlightedsky7239_db_user:5hu6rjoTezOHu0wV@cluster0.dbbcipx.mongodb.net/?appName=Cluster0")
        client.server_info()
        print("successfully connected to mongo db")

    except Exception as e:
        print("Could not connect")
        print("error",e)
        return 
    
    db=client["agriculture_app"]
    collection=db["fields_telemetry"]

    collection.delete_many({})
    '''
    print("\n-- 1.Insert operation --")

    farmer_data={
        "farmer_id":101,
        "name":"anchu",
        "district":"kamrup",
        "credit_points":100,
        "active_plots":["block-a","block-b"]
    }

    insert_result=collection.insert_one(farmer_data)
    print(f"inserted doc id:{insert_result.inserted_id}")

    more_farmer=[
        {"farmer_id":102,"name":"arman","district":"jorhat","credit_points":100,"active_plots":["block-c"]},
        {"farmer_id":103,"name":"rahul","district":"kamrup","credit_points":99,"active_plots":[]}
    ]

    collection.insert_many(more_farmer)
    print("multiple data added..")

    print("\n-- read operations--")
    query_single=collection.find_one({"name":"anchu"})
    print(query_single)

    print("\n-- farmers in kamrup district--")
    query_multiple=collection.find({"district":"kamrup"})
    for i in query_multiple:
        print(f"-{i['name']} has {i['credit_points']}points.")
'''
    for i in collection.find():
        print(i)

    client.close()

if __name__=="__main__":
    run_mongodb_demo()