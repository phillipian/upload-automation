import json

class StudentDirectory:
    def __init__(self, student_dict):
        self.student_dict = student_dict
        self.dorm_list = []
        self.location_list = []
        for student in self.student_dict.values():
            if student['living_location'] not in self.dorm_list:
                self.dorm_list.append(student['living_location'])
            if student['location'] not in self.location_list:
                self.location_list.append(student['location'])
        self.class_list = ['junior', 'lower', 'upper', 'senior']
    def search_by_name(self, first_name='', last_name=''):
        student_list = []
        for student in self.student_dict:
            if last_name in student.split(',')[0] and first_name in student.split(',')[1]:
                student_list.append(student)
        return student_list 
    def list_by_class(self, class_name):
        assert class_name.lower() in self.class_list, "Error: Class name must be Junior, Lower, Upper, or Senior" 
        student_list = []
        for student in self.student_dict:
            if self.student_dict[student]['class'].lower() == class_name.lower():
                student_list.append(student)
        return student_list
    def list_by_dorm(self, dorm_name):
        student_list = []
        for student in self.student_dict:
            if dorm_name.lower() in self.student_dict[student]['living_location'].lower():
                student_list.append(student)
        return student_list
    def list_by_hometown(self, hometown):
        student_list = []
        for student in self.student_dict:
            if hometown.lower() in self.student_dict[student]['location'].lower():
                student_list.append(student)
        return student_list
    def list_by_enter_year(self, enter_year):
        student_list = []
        for student in self.student_dict:
            if int(self.student_dict[student]['enter_year']) == enter_year:
                student_list.append(student)
        return student_list

