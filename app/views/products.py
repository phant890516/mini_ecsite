from flask import Blueprint, render_template, request, session, redirect, url_for
from app.db import DatabaseManager
import math
import json
products_bp = Blueprint('products', __name__, url_prefix='/products')

# --- common paramaters ---

def check_admin():
    # check if user is authority
    role = session.get('role')
    if role == "admin":
        return True
    else:
        return False
def check_login():
    # check if user is login
    login_success = session.get('ID')
    if login_success:
        return True
    else:
        return False

# --- features for normal users ---

@products_bp.route('/')
def list():
    # show product list
    # check user
    username = session.get('username')
    role = session.get('role')
    
    # check keyword
    keyword = request.args.get('keyword')
    if not keyword:
        keyword = ''
    
    sql = "SELECT * FROM products"
    params =[]
    # if having keyword
    if keyword:
        sql += "WHERE name LIKE %s"
        params.append("%" + keyword + "%")
    
    # now page
    page_str = request.args.get('page')
    if page_str:
        page = int(page_str)
    else:
        page = 1

    # total amounts of products
    sql_count = "SELECT COUNT(*) as count FROM products"
    if keyword:
        sql_count += " WHERE name LIKE '%" + keyword + "%'"
        
    # connect to Database   
    db = DatabaseManager()
    products = []
    db.connect()
    # get products
    if db.connection:
        total = db.query(sql_count,None,True)
        print("total",total)
        # total_count = total
        total_count = total['count']       
        # sql = "SELECT * FROM products;"
        # products = db.query(sql,params,False)
        # print("products",products)
    db.disconnect()
    
    # calculate total pages
    limit = 10
    total_pages = math.ceil(total_count/limit)
    
    #OFFSET
    offset = (page -1)*limit

    # get showing products
    sql_select = "SELECT * FROM products"
    if keyword:
        sql_select += " WHERE name LIKE '%" + keyword + "%'"
    
    # limit range of showing products
    sql_select += " LIMIT " + str(limit) + " OFFSET " + str(offset)
    # connect to Database    
    db = DatabaseManager()
    products_data = []
    db.connect()
    if db.connection:
        products_data = db.query(sql_select,None,False)
        print("product_data",products_data)
    db.disconnect()
    
    return render_template("products/products.html" , products = products_data , keyword = keyword , total_pages = total_pages , current_page = page ,username = session.get('username'),role = session.get('role'),ID = session.get('ID'))


@products_bp.route('/detail/<int:id>',methods =['GET'])
def detail(id):
    # show products detail
    sql="SELECT * FROM products WHERE id = %s"
    db = DatabaseManager()
    db.connect()
    params = (id,)
    if db.connection:
        product = db.query(sql,params,True)
        print("product",product)
    db.disconnect()
    
    return render_template("products/product_detail.html" ,product = product,username = session.get('username'),role = session.get('role'),ID = session.get('ID'))

@products_bp.route('/add_cart/<product_id>', methods=['POST'])
def add_cart(product_id):
    check_login()
    if not check_login():
        return(render_template('index.html'))
    # cart function
    db = DatabaseManager()
    db.connect()
    if db.connection:
        sql_add = "SELECT * FROM products WHERE id = %s"
        params = (product_id,)
        add_product = db.query(sql_add,params,True)
        print("add_to_cart",add_product)
    db.disconnect()

    try:
        price = int(add_product['price'])
    except Exception:
        try:
            price = int(float(add_product['price']))
        except Exception:
            price = 0
    # get name , id , price of adding products
    new_item={
        "name":add_product.get("name"),
        "id":add_product.get("id"),
        "price":price,
        "count":1,
        "subtotal":price
    }
    # get cart session 
    cart_json = session.get('cart_json', [])
    if cart_json:
        cart_list = json.loads(cart_json)
    else:
        cart_list = []
    # check if products exist
    FOUND = False
    for item in cart_list:
        if new_item["id"] == item["id"]:
            item["count"] =  int(item.get('count', 1)) + 1
            item["subtotal"] = int(item.get('price')) * item["count"]
            FOUND = True
            break
        
    if not FOUND:
        cart_list.append(new_item)
    
    # change format to json
    cart_json = json.dumps(cart_list)
    
    # update session
    session["cart_json"] = cart_json
        
    return redirect(url_for('products.list'))

@products_bp.route('/update_cart/<product_id>', methods=['POST'])
def update_cart(product_id):
    # update cart
    check_login()
    if not check_login():
        return render_template('index.html')
    new_count = request.form.get('count')
    new_count = int(new_count)
    
    cart_json = session.get('cart_json',[])
    cart_list = json.loads(cart_json)
    updated=[]
    for item in cart_list:
        if str(item.get('id')) == str(product_id):
            if new_count <= 0:
                continue
            else:
                item['count'] = new_count
                item['subtotal'] = int(item['price']) * int(item['count'])
        updated.append(item)
    
    cart_list = updated
    cart_json = json.dumps(cart_list)
    session['cart_json'] = cart_json
    
    return redirect(url_for('products.cart'))

@products_bp.route('/cart/delete/<product_id>',methods =['POST'])  
def delete_from_cart(product_id):
    check_login()
    if not check_login():
        return render_template('index.html')
    
    cart_json = session.get('cart_json',[])
    cart_list = json.loads(cart_json)
    filter_list = []
    for item in cart_list:
        if str(item.get('scode'))!=str(product_id):
            filter_list.append(item)
    
    cart_list = filter_list
    cart_json = json.dumps(cart_list)
    session['cart_json'] = cart_json
    
    return redirect(url_for('products.cart'))

@products_bp.route('/cart')
def cart():
    # cart page
    check_login()
    if not check_login():
        return render_template('index.html')
    
    cart_list=[]
    
    total = 0

    if session.get('cart_json'):
        cart_json = session.get('cart_json', [])
        cart_list = json.loads(cart_json)
        for item in cart_list:
            price = int(item.get("price", 0))
            count = int(item.get("count", 0))
            subtotal = int(item.get("subtotal",0))  # 計算
            total += subtotal
    
    return render_template("products/cart.html",cart_items = cart_list,total =total,username = session.get('username'),role = session.get('role'),ID = session.get('ID'))

# --- features for authorities ---

@products_bp.route('/admin')
def admin_list():
    # admin page
    username = session.get('username')
    role = session.get('role')
    check_admin()
    if not check_admin():
        return render_template('index.html')
    check_login()
    if not check_login():
        return render_template('index.html')

    sql_products = "SELECT * FROM products"
    params =[]

    # connect to Database   
    db = DatabaseManager()
    products = []
    db.connect()
    if db.connection:
        products_data = db.query(sql_products,None,False)
        print("product_data",products_data)
    db.disconnect()
    return render_template("products/admin_items.html" , products = products_data,username = session.get('username'),role = session.get('role'),ID = session.get('ID'))

@products_bp.route('/add', methods=['GET', 'POST'])
def add():
    # upload products function
    username = session.get('username')
    role = session.get('role')
    check_admin()
    if not check_admin():
        return render_template('index.html')
    check_login()
    if not check_login():
        return render_template('index.html')
    
    if request.method == 'POST':
        #error setting
        ecnt =0
        error ={}
        stbl={
        "id":"商品番号",
        "name":"商品名",
        "price":"販売価格",
        "desicription":"商品説明",
        }

        # get data
        register = request.form
        if not register['id'].isdigit():
            error['id'] = "正整数を入力してください"
            ecnt +=1
        if not register['price'].isdigit():
            error['price'] = "正整数を入力してください"
            ecnt+=1
        
        # check if space
        for key, value in register.items():
            if not value:
                error[key] = stbl[key] + "を入力してください"
                ecnt +=1
                
        if ecnt !=0:
            return render_template('products/add.html',error = error , register = register)
        
        db = DatabaseManager()
        db.connect()
        if db.connection:   
        # check if same products exist
            sql = "SELECT * FROM lunch WHERE id = %s;"
            params = (register['id'])
            same_product = db.query(sql,params,True)
            if same_product:
                error['id'] = "同じ商品が存在する。"
                return render_template('products/add.html',error =error , register = register)
            
            data=(register['id'],register['name'],int(register['price']),register['description'])
            sql = "INSERT INTO products (id,name,price,description) VALUE (%s,%s,%s,%s)"
            register_product = db.execute(sql,data)
            if register_product:
                db.disconnect()
                return redirect(url_for('products.list'))
        
    if request.method == 'GET':
        error ={}          
        return render_template('products/add.html',error =error)

@products_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    # edit products
    username = session.get('username')
    role = session.get('role')
    check_admin()
    if not check_admin():
        return render_template('index.html')
    check_login()
    if not check_login():
        return render_template('index.html')
    
    if request.method == "GET":
        # get products data
        db  = DatabaseManager()
        product = []
        db.connect()
        if db.connection:   
            sql = "SELECT * FROM products WHERE id= %s;"
            params = (id,)
            product = db.query(sql,params,True)
            
        db.disconnect()
        error ={}
        return render_template('products/edit.html',product = product,error=error)
    
    if request.method == "POST":
        # get data
        fields = ['id','name','price','description']
        product={}
        for field in fields:
            product[field] = request.form.get(field)
            
        #error setting
        ecnt =0
        error ={}
        stbl={
        "id":"商品番号",
        "name":"商品名",
        "price":"販売価格",
        "description":"商品説明",
            }
        
        # check if space
        for key, value in product.items():
            if not value:
                error[key] = stbl[key] + "を入力してください"
                ecnt +=1

        # check if price is number
        if not product['price'].isdigit():
            error['price'] = "正整数を入力してください"
            ecnt+=1
                        
        #error event
        if ecnt !=0:             
            return render_template('products/edit.html',error = error , product = product )
        
        #update Database
        update_fields=[product['name'],int(product['price']),product['description']]
        sql = "UPDATE products set name=%s,price=%s,description=%s"
    
        sql = sql + "where id=%s;"
        update_fields.append(product['id'])
        db  = DatabaseManager()
        db.connect()
        if db.connection:
            update_product = db.execute(sql,update_fields)
        # get products data    
        db.disconnect()

    return redirect(url_for('products.admin_list'))

@products_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    # delete products
    username = session.get('username')
    role = session.get('role')
    check_admin()
    if not check_admin():
        return render_template('index.html')
    check_login()
    if not check_login():
        return render_template('index.html')
    
    db  = DatabaseManager()
    db.connect()
    if db.connection:
        # delet products function execute
        sql = "DELETE FROM products WHERE id= %s;"
        delete = db.execute(sql,(id,))
        db.disconnect()
        if delete:
            return redirect(url_for('products.admin_list'))
