from cmath import log
from code import interact
from datetime import datetime, timedelta
from hashlib import new
from time import perf_counter, time
from tkinter import Widget
from django import forms
from django.http import HttpResponseNotAllowed
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
import json
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from jdatetime import date
from django.contrib.auth import authenticate,login,logout
from django.core.files import File


from .models import Stand,Order

def index(request):
    return render(request,"karma/index.html")

def stand(request):
    stands = Stand.objects.values_list("id", "name")
    return render(request,"karma/stand.html",{"stands" : stands})

def frame(request):
    return render(request,"karma/frame.html")

def calcFrame(request):

    data = request.POST['data']

    ld = json.loads(data)
    res = {}
    for list in ld:
        if list[0] in res.keys():
            res[list[0]] += list[2] * 2
        else:
            res[list[0]] = list[2] * 2
        
        if list[1] in res.keys():
            res[list[1]] += list[2] * 2
        else:
            res[list[1]] = list[2] * 2
    res  = dicSort(cast(res))
    return render(request,"karma/show.html",{"sizes" : res})

def calcStand(request):

    res = {}

    if request.method == "POST":
        stands = []
        for i in request.POST:
            
            try :
                stand = Stand.objects.get(pk=int(i))
                number = int(request.POST[i])
            except ValueError:
                continue
            sizes = json.loads(stand.sizes)

            stands.append((stand.name , number ))
          
            
            for size in sizes:
                
                if size in res.keys():
                    
                    res[size] = res[size] + (number * int(sizes[size]))
                else:
                    res[size] = number * int(sizes[size])
                
    res  = dicSort(cast(res))
    return render(request,"karma/show.html",{'sizes' : res,"stands" : stands})

def cast(dic):
    res = {}
    for key in dic:
        try:
            x = int(key)
        except :
            x = float(key)
        res[x] = dic[key]
    return res

def dicSort(a):
    b = {}
    i = a.items()
    s = sorted(i,reverse=True)
    for q1,q2 in s:
        b[q1] = q2
    return b

@login_required(login_url='/login')
def orders(request):
    user = request.user.username
    
 #   if request.method == "POST":
 #       id = request.POST['id']
 #       order = Order.objects.get(pk=id)
 #       if 'val' in request.POST:
 #           order.workers.add(request.user)
 #       else:
 #           order.workers.remove(request.user)
    
    qo = Order.objects.filter()
    orders = []
    

    for q in qo:
        o = {}

        
        o['id'] = q.pk
        o['name'] = q.name
        o['date'] = q.date
        o['fee'] = q.fee
        o['price'] = q.price
        o['finishdate'] = q.finishdate
        o['done'] = q.done
        o['paid'] = q.paid
        o['des'] = q.des
        o['nday'] = q.daynumber
        if request.user in q.workers.all():
            pers = "true"
        else:
            pers = "false"
        o['pers'] = pers
        w = ""
        for q1 in q.workers.all():
            w += str(q1) + " | "
        w = w[:-2]
        o['by'] = w
        orders.append(o)
        
    resorder = list(reversed(orders))

    if request.user.has_perm('main.add_order'):
        return render(request,"karma/orders.html",{"username" : user,"orders" : resorder ,"showbtn" : True})

    return render(request,"karma/orders.html",{"username" : user,"orders" : resorder })

@login_required(login_url='/login')
def addorder(req) :
    if not req.user.has_perm('main.add_order'):
        raise PermissionDenied
    form = formaddorder(req.POST or None ,req.FILES or None)

    if form.is_valid():
        form.save()
        return redirect("/profile")

    return render(req,"karma/neworder.html",{'form' : form ,'userfirstname' : req.user.username})

def logoutuser(request):
    if not request.user.is_authenticated:
        return HttpResponseNotAllowed("You need to login first!")
    logout(request)
    return redirect("/orders")

def loginuser(req):
    if req.method == "POST":
       
        
        uname = req.POST['uname']
        passw = req.POST['pswd']
        user = authenticate(username=uname,password=passw)
        if user == None:
            return render(req,"auth/login.html",{"wrong" : True})
        login(req,user)
        return redirect("/orders")
    return render(req,"auth/login.html")

def passchange(request):
    if not request.user.is_authenticated:
        return HttpResponseNotAllowed("You need to login first!")
    user = request.user
    if request.method == "POST":

        if authenticate(username=user.username,password=request.POST["pass"]):
            if request.POST["newpass"] == request.POST["newpassr"]:

                user.set_password(request.POST["newpass"])
                user.save()
                return redirect("/orders")
            else:
                
                return render(request,"auth/changepass.html",{"wrongreap" : True})
        else:
            return render(request,"auth/changepass.html",{"wrong" : True})

    return render(request,"auth/changepass.html")

@login_required(login_url='/login')
def profile(req):
    context = {}
    context['username'] = req.user.username

    if req.user.has_perm("main.add_order"):

        if req.method == "GET":
            if 'done' in req.GET:
                sdate = req.GET['date']
                nday = req.GET['days']
                id = req.GET['done']
                order = Order.objects.get(pk=id)
                order.done = True
                order.finishdate = date(int(sdate[:4]),int(sdate[5:7]),int(sdate[8:])).togregorian()
                order.daynumber = int(nday)
                order.save()
            elif 'pay' in req.GET:
                id = req.GET['pay']
                order = Order.objects.get(pk=id)

                order.paid = True
                order.save()
            elif 'changegain' in req.GET:
                f = open("data.json",'w+')
                jsonfile = File(f)
                try:
                    perworker = json.loads(jsonfile.read())['perWorker']
                except:
                    perworker = 0

                cgain = req.GET['changegain']
                data = {"gain" : cgain,"perWorker" : perworker}
                jsonfile.write(json.dumps(data))
                jsonfile.close()
            elif 'changeperworker' in req.GET:
                f1 = open("data.json",'r+')
                jsonfile1 = File(f1)
                
                gain = json.loads(jsonfile1.read())['gain']
                
                    
                
                perworker = req.GET['changeperworker']
                data = {"gain" : gain,"perWorker" : perworker}
                jsonfile1.write(json.dumps(data))
                print(json.dumps(data))
                jsonfile1.close()

                
        if req.method == "POST":
            data = req.POST.copy()
            id = data.pop("idorder")
            ldate = data.pop("date")
            nday = data.pop("nday")
            done = data.pop("done")[0]
            del(data['csrfmiddlewaretoken'])
            order = Order.objects.get(pk=id[0])
            if done == "true":
                order.done = True

            sdate = ldate[0]
            order.finishdate =  date(int(sdate[:4]),int(sdate[5:7]),int(sdate[8:])).togregorian()
            order.daynumber = nday[0]
            order.workers.clear()
            jdata = {}
            for user in data:
                
                if data[user] == '' or data[user] == '0':
                    
                    continue
                order.workers.add(User.objects.all().get(username=user))
                jdata[user] = data[user]

            jsondata = json.dumps(jdata)
            order.perworker = jsondata
            order.save()
        notpaidorders = Order.objects.filter(done=True).filter(paid=False).order_by('-finishdate')
        neworders = Order.objects.filter(done=False).filter(paid=False).order_by('-date')
        hisorders = Order.objects.filter(done=True).filter(paid=True).order_by('-finishdate')
        
        
        for i in range(len(hisorders)):
            
            if req.user not in hisorders[i].workers.all():
                continue
            try:
                workerpercent = json.loads(str(hisorders[i].perworker))
            except json.JSONDecodeError:
                hisorders[i].tokenfee = 0
                continue

            per = workerpercent[req.user.username]
            hisorders[i].tokenfee = roundprice(int(int(per) / 100 * hisorders[i].fee))

        for i in range(len(notpaidorders)):
            workers = notpaidorders[i].workers.all()
            userworkers = []
            for w in workers:
                userworkers.append(w.username)
                
            notpaidorders[i].userworkers = json.dumps(userworkers)
        allusers = []
        for user in User.objects.all():
            if user.username == "superuser":
                continue
            allusers.append(user.username)
        
        context['allusers'] = allusers
        context['neworders'] = neworders
        context['doneorders'] = notpaidorders
        context['hisorders'] = hisorders
        

        mali = {}
        his = []
        today = datetime.date(datetime.now())
        starttime = datetime.date(getpervmonth(today))      
        ors = Order.objects.filter(done=True).filter(finishdate__range=[starttime,today])
        curm = 0
        
        f = open("data.json",'r+')
        jsonfile = File(f)
        print(jsonfile.read())
        print(json.loads(str(jsonfile.read())))
        gain = int(json.loads(jsonfile.read())['gain'])
        perworker = int(json.loads(jsonfile.read())['perWorker'])
        try:
            gain = int(json.loads(jsonfile.read())['gain'])
            perworker = int(json.loads(jsonfile.read())['perWorker'])
        except:
            f.write(json.dumps({'gain' : 20}))
            print('here')
            gain = 20
            perworker = 0
        for o in ors:
            curm += o.price * gain / 100

        curm = int(curm)
        
        mali['cur'] = roundprice(curm)

        jsonfile.close( )
        month = 1
        datestart = datetime.date(getpervmonth(starttime))
        dateend = getpervday(starttime)

        while (month != 12):
            ors = Order.objects.filter(done=True).filter(finishdate__range=[datestart,dateend])
            curm = 0
            for o in ors:
                curm += o.price * gain / 100
            if curm != 0:
                his.append((getnamemonth(o.finishdate.month), roundprice(curm)))
            dateend = getpervday(datestart)
            datestart = datetime.date(getpervmonth(datestart))
            month += 1
        

        mali['his'] = his
        context['mali'] = mali
        context['gain'] = gain 
        context['perworker'] = perworker 
        return render(req,"karma/profilesuser.html",context)
    else:  


        neworder = Order.objects.filter(done=False).order_by('-finishdate')
        others = Order.objects.exclude(done=False).order_by('-finishdate')
     
        hisorder = []

        for o in others:
            order = {}
            order['name'] = o.name
            order['allfee'] = o.fee
            pp = 0
            if req.user in o.workers.all():
                pp = int(json.loads(o.perworker)[req.user.username])
            order['fee'] = roundprice(int(o.fee) * pp / 100)
            order['percent'] = pp
            order['date'] = o.finishdate
            if o.paid:
                order['status'] = 'تصفیه شده'
            else:
                order['status'] = 'تصفیه نشده'
            order['nod'] = o.daynumber
            hisorder.append(order)

        context['hisorder'] = hisorder
        context['neworder'] = neworder

        mali = {}
        his = []
        today = datetime.date(datetime.now())
        starttime = datetime.date(getpervmonth(today))      
        ors = Order.objects.filter(done=True).filter(finishdate__range=[starttime,today])
        curm = 0
        for o in ors:
            if req.user in o.workers.all():
                pp = json.loads(o.perworker)[req.user.username]
                curm += o.price * pp / 100
        curm = int(curm)
        
        mali['cur'] = curm
        
        month = 1
        datestart = datetime.date(getpervmonth(starttime))
        dateend = getpervday(starttime)

        while (month != 12):
            ors = Order.objects.filter(done=True).filter(finishdate__range=[datestart,dateend])
            curm = 0
            for o in ors:
                
                if req.user in o.workers.all():
                    pp = int(json.loads(o.perworker)[req.user.username])
                    curm += o.price * pp / 100
            if curm != 0:
                his.append((getnamemonth(o.finishdate.month), curm))
            dateend = getpervday(datestart)
            datestart = datetime.date(getpervmonth(datestart))
            month += 1
        mali['his'] = his
        context['mali'] = mali


        return render(req,"karma/profileuser.html",context)
    

def getpervmonth(date):
    if date.month == 1:
        return datetime(date.year-1,12,21)      
    else:
        return datetime(date.year,date.month-1,21)
def getpervday(date):
    return date - timedelta(days=1)

def getnamemonth(m):
    months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
    return months[m-1]
def roundprice(price):
    return int(price / 1000) * 1000   
class formaddorder(forms.ModelForm):
    des = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ['name','price','des'] 
        labels = {'name' : "عنوان سفارش",'price' : "قیمت سفارش",'des' : "توضیحات"}  
 