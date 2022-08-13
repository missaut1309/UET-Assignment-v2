from tokenize import group
from .models import *
import numpy as np
import scipy.optimize
import math
from ortools.linear_solver import pywraplp

def calc_heuristic(relevancy_1, relevancy_2):
    n = len(relevancy_1)
    result = 0 
    for i in range(n):
        result += abs(relevancy_1[i] - relevancy_2[i])
    result =  (1 - result / (4 * n)) * 100
    return result

def find_max(H):
    i_max = 0
    j_max = 0
    max_value = 0
    n = len(H)
    for i in range(n):
        for j in range(n):
            if(H[i][j] >= H[i_max][j_max]):
                max_value = H[i][j]
                i_max = i
                j_max = j
    return max_value, i_max, j_max

def make_H_matrix(group_list):
    n = len(group_list)
    H = np.zeros((n, n), dtype=np.double)

    for i in range(n):
        for j in range(n):
            if(i < j):
                if(len(group_list[i].member_list)+len(group_list[j].member_list) <= 10): #group_threshold
                    H[i, j] = calc_heuristic(group_list[i].relevancy, group_list[j].relevancy)
    return H

def make_group(topic_list):
    group_list = []
    for topic in topic_list:
        group_list.append(Group(topic))
    # i=0
    # for group in group_list:
    #     print("group=%d, relevancy:"%(i))
    #     print(group.relevancy)
    #     i+=1
    H = make_H_matrix(group_list)
    # print(H)
    max_value, i_max, j_max = find_max(H)
    #print("max_value=%f, i_max=%d, j_max=%d" %(max_value, i_max, j_max))
    while(max_value >= 60): #heuristic_threshold
        print("nhóm %d - max_value=%f" %(i_max, max_value))
        for tp in group_list[j_max].member_list:
            group_list[i_max].add_mem(tp)
        group_list.pop(j_max)
        i=0
        for group in group_list:
            print("group=%d, relevancy:"%(i))
            print(group.relevancy)
            i+=1
        H = make_H_matrix(group_list)
        print(H)
        max_value, i_max, j_max = find_max(H)
        print("max_value=%f, i_max=%d, j_max=%d" %(max_value, i_max, j_max))

    return group_list

def calc_committee_heurisic(lecturer, group, committee):
    n = len(lecturer.relevancy)
    result = 0 
    if(committee.out_source >= 2 and lecturer.lecturer_source.work_place != 1): 
        return result
    else:
        for i in range(n):
            result += abs(lecturer.relevancy[i] - group.relevancy[i])
        result =  (1 - result / (4 * n)) * 100
    return result

def choose_chairman(group_list, lecturer_list,committee_list):
    chairman_list = []
    for lecturer in lecturer_list:
        if (lecturer.lecturer_source.work_place.id == 1 and lecturer.lecturer_source.degree.id <= 2):
            chairman_list.append(lecturer)
    print("chairman_list id")
    for lec in chairman_list:
        print("id=%d"%(lec.lecturer_source.id))
    
    if(len(chairman_list) < len(group_list)):
        print('The numbers of lecturer can be chairman is smaller than the numbers of group')
    else:
        H = np.zeros((len(chairman_list), len(group_list)), dtype=np.double)
        for i in range(len(chairman_list)):
            for j in range(len(group_list)):
                H[i,j] = -calc_heuristic(chairman_list[i].relevancy, group_list[j].relevancy)
        print(H)
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(H)
        
        assigned = []

        for r, c in zip(row_ind, col_ind):
            print("r=%d, c=%d" %(r,c))
            committee_list.append(Committee(chairman_list[r], group_list[c].group_id))
            assigned.append(chairman_list[r])
        
        for lec in assigned:
            lecturer_list.remove(lec)

def choose_vice_chairman(group_list, lecturer_list, committee_list):
    vice_list = []
    for lecturer in lecturer_list:
        if (lecturer.lecturer_source.degree.id <= 2):
            vice_list.append(lecturer)
    if(len(vice_list) < len(group_list)):
        print('The number of lecturer that can be vice chairman is smaller than the number of group')
    else:
        H = np.zeros((len(group_list), len(vice_list)), dtype=np.double)
        for i in range(len(vice_list)):
            for j in range(len(group_list)):
                H[i,j] = -calc_committee_heurisic(vice_list[i], group_list[j], committee_list[j])
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(H)

        assigned = []
        for r,c in zip(row_ind, col_ind):
            committee_list[c].set_vice_chairman(vice_list[r])
            assigned.append(lecturer_list[r])

        for lec in assigned:
            lecturer_list.remove(lec)

def choose_secretary(group_list, lecturer_list, committee_list):

    secretary_list = []
    for lecturer in lecturer_list:
        if(lecturer.lecturer_source.work_place.id == 1):
            secretary_list.append(lecturer)
    if(len(secretary_list) < len(group_list)):
        print('The number of lecturer that can be secretary is smaller than the number of group')
    else:
        H = np.zeros((len(secretary_list), len(group_list)), dtype=np.double)
        for i in range(len(secretary_list)):
            for j in range(len(group_list)):
                H[i,j] = -calc_committee_heurisic(secretary_list[i], group_list[j], committee_list[j])
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(H)

        assigned = []
        for r,c in zip(row_ind, col_ind):
            committee_list[c].set_secretary(secretary_list[r])
            assigned.append(secretary_list[r])

        for lec in assigned:
            lecturer_list.remove(lec)


def choose_member(group_list, lecturer_list, committee_list):
    if(len(lecturer_list) < 3 * len(group_list)):
        print("The number of lecturer is smaller than the number of group")
    else:
        H = np.zeros((len(lecturer_list), 3*len(group_list)), dtype=np.double)
        for i in range(len(lecturer_list)):
            for j in range(len(group_list)):
                H[i,3*j] = -calc_committee_heurisic(lecturer_list[i], group_list[j], committee_list[j])
                H[i,3*j + 1] = H[i, 3*j]
                H[i,3*j + 2] = H[i, 3*j]
        #print(H)
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(H)

        assigned = []
        for r,c in zip(row_ind, col_ind):
            h = math.ceil((c-2)/3)
            #print("r=%d, c=%d, h=%d" %(r,c,h))
            committee_list[h].add_mem(lecturer_list[r])
            assigned.append(lecturer_list[r])
        
        for lec in assigned:
            lecturer_list.remove(lec)

def assignment(lecturer_list, group_list):
    committee_list = []
    
    choose_chairman(group_list, lecturer_list, committee_list)
    
    choose_secretary(group_list, lecturer_list, committee_list)
    
    choose_member(group_list, lecturer_list,committee_list)
    #print("Hoi dong: %d, Giảng viên: %d, Nhóm: %d" %(len(committee_list), len(lecturer_list), len(group_list)))

    return committee_list

        
def assign_review(lecturer_list, topic_list, k_max):
    print("gvien: %d, topic: %d, k_max: %d" %(len(lecturer_list), len(topic_list), k_max))
    for i in range(len(lecturer_list)):
        print("%d-%s"%(i,lecturer_list[i].lecturer_source.name))
    for i in range(len(topic_list)):
        print("%d-%s"%(i,topic_list[i].member_list[0].title))
    print(len(lecturer_list) >= 2* len(topic_list))
    if(len(lecturer_list) >= 2* len(topic_list)):
        H = np.zeros((len(lecturer_list), 2 * len(topic_list)), dtype=np.double)
        for i in range(len(lecturer_list)):
            for j in range(len(topic_list)):
                if(lecturer_list[i].lecturer_source.id == topic_list[j].member_list[0].mentor_id):
                    H[i,j] = 0
                else:
                    H[i,2*j] = -calc_heuristic(lecturer_list[i].relevancy, topic_list[j].relevancy)
                H[i,2*j + 1] = H[i,2*j]
        
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(H)
        for r, c in zip(row_ind, col_ind):
            h = math.floor(c/2)
            topic = Topic.objects.get(id=topic_list[h].member_list[0].id)
            if(c%2 == 0):
                topic.review_2_id = lecturer_list[r].lecturer_source.id
            else:
                topic.review_1_id = lecturer_list[r].lecturer_source.id
            topic.save()
    #else:
    ###########################################################
        # n_lecturers = len(lecturer_list)
        # n_topics = len(topic_list)
        # H = np.zeros((n_lecturers, n_topics), dtype=np.double)
        # for i in range(len(lecturer_list)):
        #     for j in range(len(topic_list)):
        #         if(lecturer_list[i].lecturer_source.id == topic_list[j].member_list[0].mentor_id):
        #             H[i,j] = 0
        #         else:
        #             H[i,j] = -calc_heuristic(lecturer_list[i].relevancy, topic_list[j].relevancy)
        # task_size = []
        # for i in range(n_topics):
        #     task_size.append(2)

        # solver = pywraplp.Solver.CreateSolver('SCIP')

        # x = {}
        # for lecturer in range(n_lecturers):
        #     for topic in range(n_topics):
        #         x[lecturer,topic] = solver.IntVar(0, 1, f'x[{lecturer},{topic}]')

        # for lecturer in range(n_lecturers):
        #     solver.Add(
        #         solver.Sum([
        #             task_size[topic] * x[lecturer,topic] for topic in range(n_topics)
        #         ]) <= k_max
        #     )

        # for topic in range(n_topics):
        #     solver.Add(
        #         solver.Sum([x[lecturer,topic] for lecturer in range(n_lecturers)] )== 2)
            

        # objective_terms = []
        # for lecturer in range(n_lecturers):
        #     for topic in range(n_topics):
        #         objective_terms.append(H[lecturer][topic] * x[lecturer, topic])
        # solver.Minimize(solver.Sum(objective_terms))

        # status = solver.Solve()

        # if status==pywraplp.Solver.OPTIMAL or status== pywraplp.Solver.FEASIBLE:
        #     for lecturer in range(n_lecturers):
        #         for topic in range(n_topics):
        #             if(x[lecturer,topic].solution_value() > 0.5):
        #                 lec_id = lecturer_list[lecturer].lecturer_source.id
        #                 lec = Lecturer.objects.get(id=lec_id)
        #                 tp_id = topic_list[topic].member_list[0].id
        #                 tp = Topic.objects.get(id=tp_id)
        #                 if(tp.review_1_id == 1):
        #                     tp.review_1_id = lec.id
        #                 else:
        #                     tp.review_2_id = lec.id
        #                 cnt = lec.review_count 
        #                 lec.review_count = cnt+1
        #                 lec.save()
        #                 tp.save()
        # else:
        #     print("No Solutions found")
######################################################################################################
    else:
        r = math.ceil(len(2*topic_list)/len(lecturer_list))
        #print("r=%d"%(r))
        #k_min = min(r,k_max)
        #print("k_min=%d"%(k_min))
        H = np.zeros((k_max * len(lecturer_list), len(topic_list)), dtype=np.double)

        for j in range(len(topic_list)):
            h=0
            for i in range(len(lecturer_list)):
                if(lecturer_list[i].lecturer_source.id == topic_list[j].member_list[0].mentor_id):
                    H[h:(h+k_max),j] = 0
                else:
                    H[h:(h+k_max),j] = -calc_heuristic(lecturer_list[i].relevancy, topic_list[j].relevancy)
                h+= k_max
        #print(H)
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(H)
        #print("FOR r,c")
        for r,c in zip(row_ind, col_ind):
            #print("r=%d, c=%s"%(r,c))
            h = math.floor(r/k_max)
            lecturer_id = lecturer_list[h].lecturer_source.id
            topic = Topic.objects.get(id=topic_list[c].member_list[0].id)
            
            lecturer = Lecturer.objects.get(id=lecturer_id)
            #print("h=%d - lec_id=%d - topic_id=%s "%(h, lecturer.id, topic.id))
            rv_count = lecturer.review_count
            rv_count += 1
            lecturer.review_count = rv_count
            lecturer.save()
            topic.review_1_id = lecturer.id
            topic.save()
        for r,c in zip(row_ind, col_ind):
            h = math.floor(r/k_max)
            lecturer_id = lecturer_list[h].lecturer_source.id
            topic = Topic.objects.get(id=topic_list[c].member_list[0].id)    
            lecturer = Lecturer.objects.get(id=lecturer_id)
            #print("h=%d - lec_id=%d - lec_rv=%s "%(h, lecturer_list[h].lecturer_source.id, lecturer_list[h].lecturer_source.review_count))
            #print("h_n=%d - lec_id_n=%d - lec_rv_n=%s "%(h, lecturer.id, lecturer.review_count))

        n=0
        capa = []

        #print("capa")
        for i in range(len(lecturer_list)):
                lecturer_id = lecturer_list[i].lecturer_source.id
                lecturer = Lecturer.objects.get(id=lecturer_id)
                h = k_max - lecturer.review_count
                #print("lec_id_n=%d, rv_n=%d"%(lecturer.id,lecturer.review_count))
                n+=h
                capa.append(h)
        #print("n=%d"%(n))
        H=np.zeros((n, len(topic_list)), dtype=np.double)
        
        for j in range(len(topic_list)):
            
            h=0
            for i in range(len(lecturer_list)):
                
                capacity = capa[i]
                topic = Topic.objects.get(id=topic_list[j].member_list[0].id)
                lecturer = Lecturer.objects.get(id=lecturer_list[i].lecturer_source.id)
                #print("topic_id=%d, lec_id= %d, capa=%d, topic_mentor=%d, topic_rv1=%d"%(topic_list[j].member_list[0].id,lecturer_list[i].lecturer_source.id,capacity,topic_list[j].member_list[0].mentor_id,topic_list[j].member_list[0].review_1_id))
                #print("topic_id_n=%d, lec_id_n= %d, capa_n=%d, topic_mentor_n=%d, topic_rv1_n=%d"%(topic.id,lecturer.id,capacity,topic.mentor_id,topic.review_1_id))

                if((lecturer_list[i].lecturer_source.id == topic_list[j].member_list[0].mentor_id) or (lecturer_list[i].lecturer_source.id == topic_list[j].member_list[0].review_1_id)):
                    H[h:(h+capacity),j] = 0
                else:
                    H[h:(h+capacity),j] = -calc_heuristic(lecturer_list[i].relevancy, topic_list[j].relevancy)                
                h += capacity
        lecturer_name_map={}
        
        h=0
        for i in range(len(lecturer_list)):

            capacity = capa[i]
            #print("%d - %s - capacity: %d" %(lecturer_list[i].lecturer_source.id,lecturer_list[i].lecturer_source.name, capacity))
            for j in range(h, h + capacity):
                lecturer_name_map[j] = i
            h+=capacity
        #print(lecturer_name_map)

        row_ind, col_ind = scipy.optimize.linear_sum_assignment(H)
        for r,c in zip(row_ind, col_ind):
            h = lecturer_name_map[r]
            lecturer_id = lecturer_list[h].lecturer_source.id
            topic = Topic.objects.get(id=topic_list[c].member_list[0].id)
            lecturer = Lecturer.objects.get(id=lecturer_id)
            review_count = lecturer.review_count
            review_count += 1
            lecturer.review_count = review_count
            lecturer.save()
            topic.review_2_id = lecturer.id
            topic.save()


    
    
