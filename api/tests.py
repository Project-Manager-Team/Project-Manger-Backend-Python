from django.test import TestCase
from api.project.models import Project
# Create your tests here.
class MyTestCase(TestCase):
    def checkQuery(self):
        all = Project.objects.all()
        query = """
            select * from Project
        """
        
        result = Project.objects.raw(
           query 
        )