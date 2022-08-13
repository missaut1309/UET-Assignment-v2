from ast import Str
from multiprocessing import context
from io import StringIO
import xlsxwriter
from urllib import request
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from .models import *
from .algorithm import *
import numpy as np
from django.urls import reverse_lazy,reverse
# Create your views here.
def index(request):
    return render(request, 'assign/base.html')
def grouping(request):
    topic_list = Topic.objects.filter(status=True).order_by("-create_date")
    for topic in topic_list:
        topic.group_id = 1
        topic.save()
    group_list = make_group(topic_list)
    for gr in group_list:
        gr_id = group_list.index(gr) + 2
        #print(gr_id)
        my_gr, created = MyGroup.objects.update_or_create(
            id=gr_id,
            defaults={'name': (gr_id-1)}
        )  
        print(my_gr.name)
        print(created)
        for mem in gr.member_list:
            mem.group = my_gr
            mem.save()
            print(mem.title)
            
        print(gr.relevancy)
        print("-----")

    my_group_list = MyGroup.objects.filter(id__gt=1).order_by("id")


    context = {
        'my_group_list': my_group_list,
    }
    
    return render(request, 'assign/grouping.html', context)

def change_test(request):
    change_list = request.POST.getlist("change")
    for change in change_list:
        a = change.split("-")
        topic_id = a[0]
        group_id = a[1]
        topic = Topic.objects.get(id=topic_id)
        topic.group_id = group_id
        topic.save()
    
    my_group_list = MyGroup.objects.filter(id__gt=1)
    context = {
        'my_group_list' : my_group_list,
    }

    return render(request, 'assign/test2.html', context)

def assign(request):
    my_lecturer_list = Lecturer.objects.filter(degree_id__lte=3, status=True)
    my_group_list = MyGroup.objects.filter(id__gt=1)
    for lecturer in my_lecturer_list:
        lecturer.committee_id = 1
        lecturer.save() 
    if(my_lecturer_list.count() < 5*my_group_list.count()):
        return redirect('cannt-assign')

    lecturer_list = []
    ###print("Lecturer List")
    for lec in my_lecturer_list:
        lecturer_list.append(LecturerV2(lec))
    group_list = []
    for gr in my_group_list:
        n = gr.topic_group.count()
        if(n>=1):
            group_list.append(GroupV2(gr.id))
    # print("Group List")
    # for gr in group_list:
    #     print(gr.group_id)
    #     print(gr.relevancy)

    committee_list = assignment(lecturer_list, group_list)
    print("Committee List")
    for com in committee_list:
        committee = MyCommittee.objects.get_or_create(group__id=com.group_id, defaults={"name": "Hoi dong", "group_id":(com.group_id)})
        for mem in com.member_list:
            lecturer = Lecturer.objects.get(id=mem.lecturer_source.id)
            lecturer.committee_id = committee[0].id
            if(com.chairman.lecturer_source.id == lecturer.id):
                #print("Chu tich: %s" %(lecturer.name))
                lecturer.position_id = 1
            elif(com.secretary.lecturer_source.id == lecturer.id):
                #print("Thu ky: %s" %(lecturer.name))
                lecturer.position_id = 3
            else:
                #print("Uy vien: %s" %(lecturer.name))
                lecturer.position_id = 4
            lecturer.save()

    context_group_list= MyGroup.objects.filter(id__gt=1)
    context = {
        'group_list': context_group_list,
    }
    return render(request,'assign/test_assign.html', context)
    

    
def LecturerList(request):
    lecturer_list = Lecturer.objects.all().order_by("-status")
    context = {
        'lecturer_list' : lecturer_list,
    }
    return render(request, 'assign/lecturer_list.html', context)

def TopicList(request):
    topic_list = Topic.objects.filter(status=False)
    context = {
        'topic_list' : topic_list,
    }
    return render(request, 'assign/topic_list.html', context)

def topic_update_form(request, pk):
    topic = Topic.objects.get(id=int(pk))
    department = Department.objects.get(id=topic.department_id)
    keyword_list = Keyword.objects.filter(department_id=department.id)
    lecturer_list = Lecturer.objects.all()
    context = {
        'topic': topic,
        'keyword_list' : keyword_list,
        'department' : department,
        'lecturer_list': lecturer_list,
    }

    return render(request,'assign/topic_update_form.html', context)

def TopicListApproved(request):
    topic_list = Topic.objects.filter(status=True)
    context = {
        'topic_list' : topic_list,
    }
    return render(request, 'assign/topic_list_approved.html', context)

def can_not_assign(request):
    return HttpResponse("<h2>Khong the thuc hien phan cong vi so giang vien < 5 lan so nhom de tai</h2>")

def change_assign_test(request):
    change_list = request.POST.getlist("change")
    change_backup = []
    for change in change_list:
        a = change.split("-")
        position_id = a[0]
        committee_id = a[1]
        lecturer_id = a[2]

        lecturer = Lecturer.objects.get(id=lecturer_id)
        change_backup.append( str(lecturer_id) + "-" + str(lecturer.position_id) + "-" + str(lecturer.committee_id) + "-" + str(position_id) + "-" + str(committee_id))   
        lecturer.position_id = position_id
        lecturer.committee_id = committee_id
        lecturer.position_status = False
        lecturer.save()
    
    committee_list = MyCommittee.objects.filter(id__gt=1)
    for com in committee_list:
        lecturer_list = Lecturer.objects.filter(committee=com)
        if(len(lecturer_list) == 0):
            continue
        elif(len(lecturer_list) == 5):
            check = 0
            for lec in lecturer_list:
                if(lec.work_place_id != 1):
                    check += 1
            if(check <= 2):
                for lec in lecturer_list:
                    lec.position_status = True
                    lec.save()
            else:
                return HttpResponse("<h1>Khong the phan cong do co 1 hoi dong co qua 2 thanh vien khong la giang vien cua truong</h1>")
        else:
            HttpResponse("<h1>Khong the thay doi do co 1 nhom co so thanh vien khong dung quy dinh</h1>")

    context_group_list= MyGroup.objects.filter(id__gt=1)
    context = {
        'group_list': context_group_list,
    }

    return render(request, 'assign/assign_change.html', context)


def topic_form(request):

    department_id = request.POST["department"]
    department = Department.objects.get(id=int(department_id))
    keyword_list = Keyword.objects.filter(department_id=department.id)
    lecturer_list = Lecturer.objects.all()

    context = {
        'department' : department,
        'keyword_list': keyword_list,
        'lecturer_list': lecturer_list,
    }

    return render(request, 'assign/topic_form.html', context)

def create_topic(request):
    topic_name = request.POST["topic_name"]
    student_name = request.POST["student_name"]
    student_id = request.POST["student_id"]
    mentor_id = request.POST["mentor"]
    department_id = request.POST["department"]
    keyword_list=Keyword.objects.filter(department_id=int(department_id))
    
    for keyword in keyword_list:
        keyword_level = request.POST["keyword_" + str(keyword.id) + "_level"]
        print('%d- %s' %(keyword.id, keyword_level))

    topic = Topic.objects.create(title=topic_name, student=student_name, mssv=student_id,mentor_id=mentor_id, department_id=department_id)
    topic.save()
    for keyword in keyword_list:
        keyword_level = request.POST["keyword_" + str(keyword.id) + "_level"]
        a = keyword_level.split('_')
        keyword_id = a[0]
        level = a[1]
        topic_to_kw = TopicToKeyword.objects.create(keyword_id=keyword_id, topic_id=topic.id, level=level)
        topic_to_kw.save()
    return render(request,'assign/create_topic_success.html')

def topic_update(request, pk):
    topic_name = request.POST["topic_name"]
    student_name = request.POST["student_name"]
    student_id = request.POST["student_id"]
    mentor_id = request.POST["mentor"]
    department_id = request.POST["department"]
    keyword_list=Keyword.objects.filter(department_id=int(department_id))  

    for keyword in keyword_list:
        keyword_level = request.POST["keyword_" + str(keyword.id) + "_level"]
        print('%d- %s' %(keyword.id, keyword_level))

    topic = Topic.objects.get(id=int(pk))
    topic.title= topic_name
    topic.student = student_name
    topic.mssv = student_id
    topic.mentor_id = mentor_id
    topic.department_id = department_id
    topic.save()
    for keyword in keyword_list:
        keyword_level = request.POST["keyword_" + str(keyword.id) + "_level"]
        a = keyword_level.split('_')
        keyword_id = a[0]
        level = a[1]
        topic_to_kw = TopicToKeyword.objects.get(keyword_id=keyword_id, topic_id=topic.id)
        topic_to_kw.level = level
        topic_to_kw.save()
    if(topic.status == True):
        return redirect("topic_list_approved")
    else:
        return redirect("topic_list_not_approve")

def lecturer_form(request):
    department_id = request.POST["department"]
    department= Department.objects.get(id=int(department_id))
    work_place_list = WorkPlace.objects.all()
    degree_list = Degree.objects.all()
    keyword_list = Keyword.objects.filter(department_id=department.id)
    context = {
        'department': department,
        'work_place_list': work_place_list,
        'degree_list': degree_list,
        'keyword_list': keyword_list,
    }
    
    return render(request, 'assign/lecturer_form.html',context)

def create_lecturer(request):
    lecturer_name = request.POST["lecturer_name"]
    work_place_id = request.POST["work_place"]
    degree_id = request.POST["degree"]
    chairman_exp = request.POST["chairman_exp"]
    secretary_exp = request.POST["secretary_exp"]
    department_id = request.POST["department"]
    keyword_list = Keyword.objects.filter(department_id=int(department_id))
    lecturer = Lecturer.objects.create(name=lecturer_name, degree_id=degree_id, work_place_id=work_place_id, chairman_exp=chairman_exp, secretary_exp=secretary_exp, department_id=department_id)
    lecturer.save()
    for keyword in keyword_list:
        keyword_level = request.POST["keyword_" + str(keyword.id) + "_level"]
        a = keyword_level.split('_')
        keyword_id = a[0]
        level = a[1]
        lecturer_to_kw = LecturerToKeyword.objects.create(keyword_id=keyword_id, lecturer_id=lecturer.id, level=level)
        lecturer_to_kw.save()
    return redirect('lecturer_list')

def topic_approve(request, pk):
    topic = get_object_or_404(Topic,id=request.POST.get('topic_id'))
    topic.status = True 
    topic.save()

    return HttpResponseRedirect(reverse('topic_list_not_approve'))

def topic_unapprove(request):
    topic = get_object_or_404(Topic,id=request.POST.get('topic_id'))
    topic.status = False
    topic.group_id=1
    topic.save()
    return HttpResponseRedirect(reverse('topic_list_approved'))

def lecturer_participate(request):
    lecturer = get_object_or_404(Lecturer,id=request.POST.get('lecturer_id'))
    lecturer.status = True
    lecturer.save()
    return HttpResponseRedirect(reverse('lecturer_list'))

def lecturer_unparticipate(request):
    lecturer = get_object_or_404(Lecturer,id=request.POST.get('lecturer_id'))
    lecturer.status = False
    lecturer.save()
    return HttpResponseRedirect(reverse('lecturer_list'))

def review_assign_form(request):
    return render(request, 'assign/review_assign_form.html')

def review_assign(request):
    k_max = int(request.POST["k_max"])
    my_lecturer_list = Lecturer.objects.filter(degree_id__lte=3, status=True).order_by("id")
    for lec in my_lecturer_list:
        lec.review_count=0
        lec.save()
    my_topic_list = Topic.objects.filter(status=True).order_by("id")
    
    if(my_lecturer_list.count() < 2):
        return HttpResponse("<h2>Không đủ số giảng viên để phân công phản biện</h2>")
    lecturer_list = []
    topic_list = []
    for lec in my_lecturer_list:
        lecturer_list.append(LecturerV2(lec))
    for topic in my_topic_list:
        topic_list.append(Group(topic))
    if(2*len(topic_list)/len(lecturer_list) > int(k_max)):
        return HttpResponse("<h2>Trọng số k quá nhỏ, tăng k để có thể phân công phản biện</h2>")
    else:
        assign_review(lecturer_list, topic_list, int(k_max))
    context = {
        'topic_list': my_topic_list,
        'lecturer_list': my_lecturer_list,
    }
    for topic in my_topic_list:

        print("%s - PB1: %s, PB2: %s" %(topic.title,topic.review_1.name, topic.review_2.name))
    return render(request, 'assign/review_assign.html', context)

def assign_choose(request):
    return render(request, 'assign/assign_choose.html')

def lecturer_department_form(request):
   department_list = Department.objects.all()
   context = {
    'department_list': department_list,
   }
   return render(request, 'assign/department_lecturer_form.html', context)

def topic_department_form(request):
   department_list = Department.objects.all()
   context = {
    'department_list': department_list,
   }
   return render(request, 'assign/department_topic_form.html', context)

def keyword_form(request):
    department_list = Department.objects.all()
    context= {
        'department_list': department_list,
    }
    return render(request, 'assign/keyword_form.html', context)

def keyword_create(request):
    department_id = request.POST["department"]
    keyword_name = request.POST["keyword_name"]
    keyword = Keyword.objects.create(content=keyword_name, department_id=department_id)
    keyword.save()
    return reverse_lazy('index')

def export_committee_xlsx(request):
    output = StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'SomeData')
    workbook.close()

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename="some_file_name.xlsx"'
    response.write(output.getvalue())
    return response

def lecturer_update_form(request):
    lecturer_id = request.POST["lecturer_id"]
    lecturer = Lecturer.objects.get(id=lecturer_id)
    work_place_list = WorkPlace.objects.all()
    department = Department.objects.get(id=lecturer.department_id)
    degree_list = Degree.objects.all()
    keyword_list = Keyword.objects.filter(department_id=department.id)
    context = {
        'lecturer': lecturer,
        'work_place_list': work_place_list,
        'department': department,
        'degree_list': degree_list, 
        'keyword_list': keyword_list,
    }
    return render(request, 'assign/lecturer_update_form.html', context)

def lecturer_update(request):
    lecturer_id=request.POST["lecturer_id"]
    lecturer_name = request.POST["lecturer_name"]
    work_place_id = request.POST["work_place"]
    department_id = request.POST["department_id"]
    degree_id = request.POST["degree"]
    chairman_exp = request.POST["chairman_exp"]
    secretary_exp = request.POST["secretary_exp"]
    keyword_list = Keyword.objects.filter(department_id=int(department_id))
    lecturer = Lecturer.objects.get(id=int(lecturer_id))
    lecturer.name = lecturer_name
    lecturer.work_place_id = work_place_id
    lecturer.degree_id = degree_id
    lecturer.chairman_exp = chairman_exp
    lecturer.secretary_exp = secretary_exp
    lecturer.save()
    for keyword in keyword_list:
        keyword_level = request.POST["keyword_" + str(keyword.id) + "_level"]
        a = keyword_level.split('_')
        keyword_id = a[0]
        level = a[1]
        lecturer_to_kw = LecturerToKeyword.objects.get_or_create(keyword_id=int(keyword_id), lecturer_id=lecturer.id)
        lecturer_to_kw.level = level
        lecturer_to_kw.save()
    return render(request, 'assign/update_lecturer_success.html')    