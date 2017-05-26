# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class SavedData(models.Model):
    result_title = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    excerpt = models.TextField(blank=True, null=True)
    article_type = models.TextField(blank=True, null=True)
    no_pages = models.IntegerField(blank=True, null=True)
    document_link = models.TextField(blank=True, null=True)
    fetched_on = models.TextField(blank=True, null=True)  # This field type is a guess.
    document_text = models.TextField(blank=True, null=True)
    pdf_url = models.TextField(blank=True, null=True)
    enhanced_on = models.TextField(blank=True, null=True)
    abstracts = models.TextField(blank=True, null=True)
    article_rank = models.IntegerField(blank=True, null=True)
    number_of_mentions = models.IntegerField(blank=True, null=True)
    normalized_number_of_mentions = models.FloatField(db_column='NORMALIZED_number_of_mentions', blank=True, null=True)  # Field name made lowercase.
    date_of_analysis = models.TextField(blank=True, null=True)
    used_search_terms = models.TextField(blank=True, null=True)
    estimated_publication_date = models.IntegerField(blank=True, null=True)
    row_id = models.IntegerField(blank=True, null=True, primary_key=True)

    class Meta:
        managed = True
        db_table = 'saved_data'
