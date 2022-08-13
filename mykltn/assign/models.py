from xmlrpc.client import boolean
from django.db import models

class WorkPlace(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Degree(models.Model):
    title = models.CharField(max_length=10)
    full_title = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.title

    
class MyGroup(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class MyCommittee(models.Model):
    name = models.CharField(max_length=20)
    group = models.ForeignKey(MyGroup,on_delete=models.CASCADE, related_name="committee_group", default=1)
    

    def __str__(self):
        return self.name

class Position(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Department(models.Model):
    name = models.CharField(max_length= 100)
    
    def __str__(self):
        return self.name

class Keyword(models.Model):
    content = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="keyword_department", default=1)

    def __str__(self) -> str:
        return self.content



class Lecturer(models.Model):
    name = models.CharField(max_length=100)
    work_place = models.ForeignKey(WorkPlace, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="lecturer_department", default=1)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    chairman_exp = models.BooleanField(default=False)
    vice_chairman_exp = models.BooleanField(default=False)
    secretary_exp = models.BooleanField(default=False)
    committee = models.ForeignKey(MyCommittee, on_delete=models.CASCADE, related_name="lecturer_committee", default=1)
    committee_status = models.BooleanField(default=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="lecturer_position", default=4)
    review_count = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    

    def __str__(self):
        return '%s %s' %(self.degree.title, self.name)

class Topic(models.Model):
    title = models.CharField(max_length=200)
    student = models.CharField(max_length=100)
    mssv = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="topic_department", default=1)
    mentor = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name="topic_mentor")
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    group = models.ForeignKey(MyGroup, on_delete=models.CASCADE, related_name="topic_group", default = 1)
    status = models.BooleanField(default=False)
    review_1 = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name="topic_review_first", default=3)
    review_2 = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name="topic_review_second", default=3)


    def __str__(self):
        return self.title


class TopicToKeyword(models.Model):
    LEVEL_CHOICES = [
        (1, 'Hoàn toàn không'),
        (2, 'Ít'),
        (3, 'Bình thường'),
        (4, 'Nhiều'),
        (5, 'Hoàn toàn có'),
    ]
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="topic_to_keyword")
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name="keyword_to_topic")
    level = models.IntegerField(choices=LEVEL_CHOICES)

    def __str__(self):
        return '%s - %s' % (self.topic.title, self.keyword.content)

class LecturerToKeyword(models.Model):
    LEVEL_CHOICES = [
        (1, 'Hoàn toàn không'),
        (2, 'Ít'),
        (3, 'Bình thường'),
        (4, 'Nhiều'),
        (5, 'Hoàn toàn có'),
    ]
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name="lecturer_to_keyword")
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name="keyword_to_lecturer")
    level = models.IntegerField(choices=LEVEL_CHOICES)

    def __str__(self):
        return '%s - %s' % (self.lecturer.name, self.keyword.content)

class Group:
    def __init__(self, first_mem: Topic) -> None:
        self.member_list = []
        self.member_list.append(first_mem)
        self.make_relevancy(first_mem)

    def make_relevancy(self, first_mem: Topic):
        m = Keyword.objects.count()
        relevancy = []
        for i in range(m):
            relevancy.append(0)
        kw_level_list = first_mem.topic_to_keyword.all().order_by("keyword_id")
        for kw_lv in kw_level_list:
            i = kw_lv.keyword.id - 1
            lv = kw_lv.level
            relevancy[i] = lv
        self.relevancy = relevancy

    def add_mem(self, mem: Topic):
        self.member_list.append(mem)
        self.update_group_relevancy(mem, False)

    def remove_mem(self, mem: Topic):
        self.member_list.remove(mem)
        self.update_group_relevancy(mem, True)

    def update_group_relevancy(self, mem: Topic, is_remove: boolean):
        mem_gr = Group(mem)
        m = Keyword.objects.count()
        if(is_remove == True):
            for i in range(m):
                self.relevancy[i] = self.relevancy[i] * 2 - mem_gr.relevancy[i]
        else:
            for i in range(m):
                self.relevancy[i] = (self.relevancy[i] + mem_gr.relevancy[i])/2

class LecturerV2:
    def __init__(self, lecturer:Lecturer):
        self.lecturer_source = lecturer
        self.make_relevancy(lecturer)

    def make_relevancy(self, first_mem: Lecturer):
        m = Keyword.objects.count()
        relevancy = []
        for i in range(m):
            relevancy.append(0)
        kw_level_list = first_mem.lecturer_to_keyword.all()
        for kw_lv in kw_level_list:
            i = kw_lv.keyword.id - 1
            lv = kw_lv.level
            relevancy[i] = lv
        self.relevancy = relevancy

class Committee:
    def __init__(self, first_mem: LecturerV2, group_id):
        self.group_id = group_id
        self.member_list = []
        self.member_list.append(first_mem)
        self.relevancy = first_mem.relevancy
        self.out_source = 0
        self.set_chairman(first_mem)
    

    def add_mem(self, mem: LecturerV2): #is_key = 1 -> chairman, is_key = 2 -> vice_chairman, is_key = 3 -> secretary, is_key = 0 -> normal
        if(mem.lecturer_source.work_place != 1):
            self.out_source += 1 
        self.member_list.append(mem)
        self.update_committee_relevancy(mem, False)

    def remove_mem(self, mem: LecturerV2):
        self.member_list.remove(mem)
        self.update_committee_relevancy(mem, True)

    def update_committee_relevancy(self,mem: LecturerV2, is_remove: boolean):
        m = Keyword.objects.count()
        if(is_remove == True):
            for i in range(m):
                self.relevancy[i] = self.relevancy[i] * 2 - mem.relevancy[i]
        else:
            for i in range(m):
                self.relevancy[i] = (self.relevancy[i] + mem.relevancy[i])/2

    def set_chairman(self, mem):
        self.chairman = mem
    
    def set_vice_chairman(self, mem):
        self.add_mem(mem)
        self.vice_chairman = mem
    
    def set_secretary(self, mem):
        self.add_mem(mem)
        self.secretary = mem 

class GroupV2:
    def __init__(self, group_id):
        self.group_id = group_id
        self.make_relevancy(group_id)

    def make_relevancy(self, group_id):
        topic_group_list = Topic.objects.filter(group_id=group_id)
        first_topic = topic_group_list.first()
        topic_group_list.exclude(id = first_topic.id)
        group = Group(first_topic)
        for topic in topic_group_list:
            group.add_mem(topic)

        self.relevancy = group.relevancy






