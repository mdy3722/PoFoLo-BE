from django.db import models
#from projects.models import Project
#from users.models import PofoloUser

# Create your models here.
class Comment(models.Model):
    writer = models.ForeignKey("users.PofoloUser", on_delete=models.CASCADE, related_name="comments")  # 댓글 작성자
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="comments")
    commented_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()  
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies") # 답글은 부모 댓글과 연결 됨. 일종의 상속 개념

    def __str__(self):
        return f"{self.writer.nickname} - {self.text[:20]}"