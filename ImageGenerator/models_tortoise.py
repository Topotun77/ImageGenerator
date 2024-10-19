from tortoise import models
from tortoise import fields


class Image(models.Model):
    id = fields.IntField(primary_key=True)
    # user_id = fields.ForeignKeyField("models.UserSettings", 'id')
    user_id = fields.IntField()
    image = fields.CharField(255, null=False)
    query_text = fields.TextField()
    date = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'KandiGen_image'

    def __str__(self):
        return f"{self.user_id} - {self.image}"


class Word(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(100, null=False, unique=True)
    count = fields.IntField(default=0)

    # images = fields.ManyToManyField('Image', related_name='words', through='KandiGen_word_image')

    class Meta:
        table = 'KandiGen_word'

    def __str__(self):
        return self.name


class UserSettings(models.Model):
    id = fields.IntField(primary_key=True)
    # user_id = fields.ForeignKeyField("auth.User")
    user_id = fields.IntField()
    day_team = fields.BooleanField(default=True)
    page_num = fields.IntField(default=9)
    age = fields.IntField(default=0)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        table = 'KandiGen_usersettings'


class Word_Image(models.Model):
    # id = fields.IntField(primary_key=True)
    word_id = fields.IntField()
    image_id = fields.IntField()
    # word_id = fields.ForeignKeyField(model_name='Word')
    # image_id = fields.ForeignKeyField(model_name='Image')

    class Meta:
        table = 'KandiGen_word_image'
        