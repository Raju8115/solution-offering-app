from sqlalchemy import create_engine, text
import urllib.parse

# URL encode password if it contains special characters
password = urllib.parse.quote_plus('opn6MIJ6W3nuMjnH')
username = 'qfk97200'
hostname = '1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud'
port = 32286
database = 'bludb'

# Create connection string
connection_string = f'ibm_db_sa://qfk97200:{password}@{hostname}:{port}/{database}?Security=SSL'

try:
    # Create engine
    engine = create_engine(connection_string)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT CURRENT DATE FROM SYSIBM.SYSDUMMY1"))
        for row in result:
            print(f"✅ Connected! Current Date: {row[0]}")
            
except Exception as e:
    print(f"❌ Error: {e}")