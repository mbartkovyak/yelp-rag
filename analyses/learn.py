class Coach:

    def __init__(self, name, sport):
        self.name = name
        self.sport = sport
        self.sessions_taught = 0
        self.student_count = 2

    def coach_sport(self):
        return f"Hi, I'm {self.name} and I train {self.sport}"
    
    def teach_session(self):
        self.sessions_taught +=1
    
    def enroll(self,n):
        self.student_count += n 
        return n


trainee1 = Coach('Anna', 'tennis')
trainee2 = Coach('Kek', 'swimming')

trainee1.teach_session()
trainee1.teach_session()
trainee1.teach_session()
trainee2.teach_session()


trainee1.enroll(5)
trainee2.enroll(3)

print(trainee1.student_count)
print(trainee2.student_count)