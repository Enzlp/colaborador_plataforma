from django.db import models
from django.contrib.postgres.fields import ArrayField

# Clase para poder traer JSON fields de manera segura
import json
class SafeJSONField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        if isinstance(value, (list, dict)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return []
        return value

# Create your models here.

class Institution(models.Model):
    id = models.TextField(primary_key=True)
    ror = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    country_code = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    homepage_url = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    image_thumbnail_url = models.TextField(blank=True, null=True)
    display_name_acronyms = SafeJSONField(blank=True, null=True)
    display_name_alternatives = SafeJSONField(blank=True, null=True)
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    works_api_url = models.TextField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)  # timestamp without timezone

    class Meta:
        db_table = 'institutions'
        managed = False


    def __str__(self):
        return str(self.display_name)

class Author(models.Model):
	id = models.TextField(primary_key=True)
	orcid = models.TextField(blank=True, null=True)
	display_name = models.TextField(blank=True, null=True)
	display_name_alternatives = SafeJSONField(blank=True, null=True)
	works_count = models.IntegerField(blank=True, null=True)
	cited_by_count = models.IntegerField(blank=True, null=True)
	last_known_institution = models.ForeignKey(
			Institution,
			on_delete=models.DO_NOTHING,
			db_column='last_known_institution',
			related_name='last_known'
	)
	works_api_url = models.TextField(blank=True, null=True)
	updated_date = models.DateTimeField(blank=True, null=True)

	class Meta: 
		db_table = 'authors'
		managed = False

	def __str__(self):
	    return str(self.id)

class AuthorCountByYear(models.Model):
	author = models.ForeignKey(
			Author,
			on_delete=models.DO_NOTHING,
			db_column='author_id',
			related_name='counts_by_year'
	)
	year = models.IntegerField()
	works_count = models.IntegerField(null=True, blank=True)
	cited_by_count = models.IntegerField(null=True, blank=True)
	oa_works_count = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'authors_counts_by_year'
		managed = False
		unique_together = (('author', 'year'),)

	def __str__(self):
		return f"{self.author} ({self.year})"	
	
class AuthorIds(models.Model):
	author = models.OneToOneField(
			Author,
			on_delete=models.DO_NOTHING,
			db_column='author_id',
			primary_key=True,
			related_name='ids'
	)
	openalex = models.TextField(blank=True, null=True)
	orcid = models.TextField(blank=True, null=True)
	scopus = models.TextField(blank=True, null=True)
	twitter = models.TextField(blank=True,null=True)
	wikipedia = models.TextField(blank=True, null=True)
	mag = models.BigIntegerField(blank=True, null=True)

	class Meta:
		db_table = 'authors_ids'
		managed = False

	def __str__(self):
		return str(self.author)
	
class Concept(models.Model):
	id = models.TextField(primary_key=True)
	wikidata = models.TextField(blank=True, null=True)
	display_name= models.TextField(blank=True, null=True)
	level = models.IntegerField(blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	works_count = models.IntegerField(blank=True, null=True)
	cited_by_count = models.IntegerField(blank=True, null=True)
	image_url = models.TextField(blank=True, null=True)
	image_thumbnail_url = models.TextField(blank=True, null=True)
	works_api_url = models.TextField(blank=True, null=True)
	updated_date = models.DateTimeField(blank=True, null=True)

	class Meta:
		db_table = 'concepts'
		managed = False
	def __str__(self):
		return f"{self.id}"

class ConceptAncestor(models.Model):
	concept = models.ForeignKey(
			Concept,
			on_delete=models.DO_NOTHING,
			db_column='concept_id',
			related_name='children'
	)
	ancestor_concept = models.ForeignKey(
			Concept,
			on_delete=models.DO_NOTHING,
			db_column='ancestor_id',
			related_name='parent'
	)

	class Meta: 
		db_table = 'concepts_ancestors'
		managed = False
	def __str__(self):
		return f"{self.concept_id} < {self.ancestor_id}"
	
class ConceptCountByYear(models.Model):
	concept = models.ForeignKey(
			Concept,
			on_delete=models.DO_NOTHING,
			db_column='concept_id',
			related_name='counts_by_year'
	)
	year = models.IntegerField(blank=True, null=True)
	works_count = models.IntegerField(blank=True, null=True)
	cited_by_count = models.IntegerField(blank=True, null=True)
	oa_works_count = models.IntegerField(blank=True, null=True)

	class Meta:
		db_table = 'concepts_counts_by_year'
		managed = False
		unique_together = (('concept', 'year'),)
	
	def __str__(self):
		return f"{self.concept} {self.year}"
	
class ConceptIds(models.Model):
	concept = models.OneToOneField(
		Concept,
		on_delete=models.DO_NOTHING,
		db_column='concept_id',
		primary_key=True,
		related_name='identifiers'
	)
	openalex = models.TextField(blank=True, null=True)
	wikidata = models.TextField(blank=True, null=True)
	wikipedia = models.TextField(blank=True, null=True)
	umls_aui = models.TextField(blank=True, null=True)
	umls_cui = models.TextField(blank=True, null=True)
	mag = models.BigIntegerField(blank=True, null=True)

	class Meta:
		db_table = 'concepts_ids'
		managed = False

	def __str__(self):
		return f"{self.concept}"

class ConceptRelatedConcept(models.Model):
	concept = models.ForeignKey(
		Concept,
		on_delete=models.DO_NOTHING,
		db_column='concept_id',
		related_name='related_to'
	)
	related_concepts = models.ForeignKey(
		Concept,
		on_delete=models.DO_NOTHING,
		db_column='related_concept_id',
		related_name='related_from'
	)
	score = models.FloatField()

	class Meta:
		db_table = 'concepts_related_concepts'
		managed = False


	def __str__(self):
			return f"{self.concept_id} <> {self.related_concept_id}"


class InstitutionAssociatedInstitution(models.Model):
	institution = models.ForeignKey(
		Institution,
		on_delete=models.DO_NOTHING,
		db_column = 'institution_id',
		related_name = 'associations'
	)
	associated_institution = models.ForeignKey(
		Institution,
		on_delete=models.DO_NOTHING,
		db_column = 'associated_institution_id',
		related_name = 'associated_by'
	)
	relationship = models.TextField(blank=True, null=True)
	
	class Meta:
			db_table = 'institution_associated_institution'
			managed = False
			unique_together = (('institution', 'associated_institution'),)  # cada par único

	def __str__(self):
			return f"{self.institution_id} <> {self.associated_institution_id} ({self.relationship})"
	
class InstitutionCountByYear(models.Model):
	institution = models.ForeignKey(
		Institution,
		on_delete=models.DO_NOTHING,
		db_column = 'institution_id',
		related_name = 'counts_by_year'
	)
	year = models.IntegerField(blank=True, null=True)
	works_count = models.IntegerField(blank=True, null=True)
	cited_by_count = models.IntegerField(blank=True, null=True)
	oa_works_count = models.IntegerField(blank=True, null=True)

	class Meta:
		db_table = 'institutions_counts_by_year'
		managed = False
		unique_together = (('institution', 'year'),)

	def __str__(self):
		return f'{self.institution} - {self.year}'
	
class InstitutionGeo(models.Model):
	institution = models.OneToOneField(
		Institution,
		on_delete=models.DO_NOTHING,
		db_column = 'institution_id',
		primary_key=True,
		related_name = 'geo'
	)
	city = models.TextField(blank=True, null=True)
	geonames_city_id = models.TextField(blank=True, null=True)
	region = models.TextField(blank=True, null=True)
	country_code = models.TextField(blank=True, null=True)
	country = models.TextField(blank=True, null=True)
	latitude = models.FloatField(blank=True, null=True)
	longitude = models.FloatField(blank=True, null=True)

	class Meta:
		db_table = 'institutions_geo'
		managed=False
	
	def __str__(self):
		return str(self.institution)
	
class InstitutionIds(models.Model):
	institution = models.OneToOneField(
		Institution,
		on_delete=models.DO_NOTHING,
		db_column = 'institution_id',
		primary_key=True,
		related_name = 'ids'
	)
	openalex= models.TextField(blank=True, null=True)
	ror = models.TextField(blank=True, null=True)
	grid = models.TextField(blank=True, null=True)
	wikipedia = models.TextField(blank=True, null=True)
	wikidata = models.TextField(blank=True, null=True)
	mag = models.BigIntegerField(blank=True, null=True)

	class Meta: 
		db_table = 'institutions_ids'
		managed = False

	def __str__(self):
		return str(self.institution)

class Publisher(models.Model):
    id = models.TextField(primary_key=True)
    display_name = models.TextField(blank=True, null=True)
    alternate_titles = SafeJSONField(blank=True, null=True)
    country_codes = SafeJSONField(blank=True, null=True)
    hierarchy_level = models.IntegerField(blank=True, null=True)
    parent_publisher = models.ForeignKey(
        'self',            
        on_delete=models.DO_NOTHING,
        db_column='parent_publisher',
        blank=True,
        null=True,
        related_name='child_publishers'  
    )
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    sources_api_url = models.TextField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)  
    class Meta:
        db_table = 'publishers'
        managed = False

    def __str__(self):
        return str(self.display_name)
		
class PublisherCountByYear(models.Model):
	publisher = models.ForeignKey(
		Publisher,
		on_delete=models.DO_NOTHING,
		db_column = 'publisher_id',
		related_name = 'counts_by_year'
	)
	year = models.IntegerField(blank=True, null=True)
	works_count = models.IntegerField(blank=True, null=True)
	cited_by_count = models.IntegerField(blank=True, null=True)
	oa_works_count = models.IntegerField(blank=True, null=True)

	class Meta:
		db_table = 'publishers_counts_by_year'
		managed = False
		unique_together = (('publisher', 'year'),)

	def __str__(self):
		return f'{self.publisher} - {self.year}'

class PublisherIds(models.Model):
	publisher = models.OneToOneField(
		Publisher,
		on_delete=models.DO_NOTHING,
		db_column = 'publisher_id',
		primary_key=True,
		related_name = 'ids'
	)
	openalex= models.TextField(blank=True, null=True)
	ror = models.TextField(blank=True, null=True)
	wikidata = models.TextField(blank=True, null=True)

	class Meta: 
		db_table = 'publishers_ids'
		managed = False

	def __str__(self):
		return str(self.publisher)
	
class Source(models.Model):
    id = models.TextField(primary_key=True)
    issn_l = models.TextField(blank=True, null=True)
    issn = SafeJSONField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    publisher = models.TextField(blank=True, null=True)  
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    is_oa = models.BooleanField(null=True)         
    is_in_doaj = models.BooleanField(null=True)    
    homepage_url = models.TextField(blank=True, null=True)
    works_api_url = models.TextField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'sources'
        managed = False

    def __str__(self):
        return str(self.display_name)

		
class SourceCountByYear(models.Model):
	source = models.ForeignKey(
		Source,
		on_delete=models.DO_NOTHING,
		db_column = 'source_id',
		related_name = 'counts_by_year'
	)
	year = models.IntegerField(blank=True, null=True)
	works_count = models.IntegerField(blank=True, null=True)
	cited_by_count = models.IntegerField(blank=True, null=True)
	oa_works_count = models.IntegerField(blank=True, null=True)

	class Meta:
		db_table = 'sources_counts_by_year'
		managed = False
		unique_together = (('source', 'year'),)

	def __str__(self):
		return f'{self.source} - {self.year}'

class SourceIds(models.Model):
	source = models.OneToOneField(
		Source,
		on_delete=models.DO_NOTHING,
		db_column = 'source_id',
		primary_key=True,
		related_name = 'ids'
	)
	openalex= models.TextField(blank=True, null=True)
	issn_l = models.TextField(blank=True, null=True)
	issn = SafeJSONField(blank=True, null=True)
	mag = models.BigIntegerField(blank=True, null=True)
	wikidata = models.TextField(blank=True, null=True)
	fatcat = models.TextField(blank=True, null=True)

	class Meta:
		db_table = 'sources_ids'
		managed = False

	def __str__(self):
		return str(self.source)
	
class Work(models.Model):
    id = models.TextField(primary_key=True)
    doi = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publication_date = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    is_retracted = models.BooleanField(null=True)
    is_paratext = models.BooleanField(null=True)
    cited_by_api_url = models.TextField(blank=True, null=True)
    abstract_inverted_index = SafeJSONField(blank=True, null=True)
    language = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'works'
        managed = False

    def __str__(self):
        return str(self.title)

class WorkAuthorship(models.Model):
    work = models.ForeignKey(
			Work,
			on_delete=models.DO_NOTHING,
			db_column = 'work_id',
			related_name = 'authorships'
		) 
    author_position = models.TextField(blank=True, null=True)
    author= models.ForeignKey(
			Author,
			on_delete=models.DO_NOTHING,
			db_column = 'author_id',
			related_name = 'work_authorships'
		) 
    institution= models.ForeignKey(
			Institution,
			on_delete=models.DO_NOTHING,
			db_column = 'institution_id',
			related_name = 'authorship_affiliations'
		) 
    raw_affiliation_string = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'works_authorships'
        managed = False



class WorksBestOaLocation(models.Model):
		work = models.ForeignKey(
			Work,
			on_delete=models.DO_NOTHING,
			db_column = 'work_id',
			related_name = 'best_oa_location'
		) 
		source = models.ForeignKey(
			Source,
			on_delete=models.DO_NOTHING,
			db_column = 'source_id',
			related_name = 'works_best_oa'
		) 
		landing_page_url = models.TextField(null=True, blank=True)
		pdf_url = models.TextField(null=True, blank=True)
		is_oa = models.BooleanField(null=True, blank=True)
		version = models.TextField(null=True, blank=True)
		license = models.TextField(null=True, blank=True)

		class Meta:
				db_table = 'works_best_oa_locations'
				managed = False


		def __str__(self):
				return f"OA Location for {self.work}"
		
class WorkBiblio(models.Model):
	work = models.OneToOneField(
		Work,
		on_delete=models.DO_NOTHING,
		db_column= 'work_id',
		primary_key=True,
		related_name = 'biblio'
	)
	volume = models.TextField(null=True, blank=True)
	issue = models.TextField(null=True, blank=True)
	first_page = models.TextField(null=True, blank=True)
	last_page = models.TextField(null=True, blank=True)

	class Meta:
		db_table = 'works_biblio'
		managed = False

	def __str__(self):
		return f"{self.work}"
	
class WorkConcept(models.Model):
	work = models.ForeignKey(
		Work,
		on_delete=models.DO_NOTHING,
		db_column = 'work_id',
		related_name = 'work_concepts'
	) 
	concept = models.ForeignKey(
		Concept,
		on_delete=models.DO_NOTHING,
		db_column = 'concept_id',
		related_name = 'work_concepts'
	) 
	score = models.FloatField(null=True, blank=True)

	class Meta:
		db_table = 'works_concepts'
		managed = False


	def __str__(self):
			return f"Work {self.work_id} - Concept {self.concept_id} (score: {self.score})"
	
class WorksIds(models.Model):
	work = models.OneToOneField(
		Work,
		on_delete=models.DO_NOTHING,
		db_column= 'work_id',
		primary_key=True,
		related_name = 'work_ids'
	)
	openalex = models.TextField(null=True, blank=True)
	doi = models.TextField(null=True, blank=True, db_index=True)
	mag = models.BigIntegerField(null=True, blank=True)
	pmid = models.TextField(null=True, blank=True)
	pmcid = models.TextField(null=True, blank=True)

	class Meta:
			db_table = 'works_ids'
			managed = False


	def __str__(self):
			return f"IDs for {self.work}"
		
class WorksLocation(models.Model):
			work = models.ForeignKey(
				Work,
				on_delete=models.DO_NOTHING,
				db_column = 'work_id',
				related_name = 'locations'
			) 
			source = models.ForeignKey(
				Source,
				on_delete=models.DO_NOTHING,
				db_column = 'source_id',
				related_name = 'work_locations'
			) 
			landing_page_url = models.TextField(null=True, blank=True)
			pdf_url = models.TextField(null=True, blank=True)
			is_oa = models.BooleanField(null=True, blank=True)
			version = models.TextField(null=True, blank=True)
			license = models.TextField(null=True, blank=True)

			class Meta:
					db_table = 'works_locations'
					managed = False

			def __str__(self):
					return f"Location for {self.work}"
			
class WorksMesh(models.Model):
	work = models.OneToOneField(
		Work,
		on_delete=models.DO_NOTHING,
		db_column = 'work_id',
		primary_key=True,
		related_name = 'mesh_terms'
	) 
	descriptor_ui = models.TextField(null=True, blank=True)
	descriptor_name = models.TextField(null=True, blank=True)
	qualifier_ui = models.TextField(null=True, blank=True)
	qualifier_name = models.TextField(null=True, blank=True)
	is_major_topic = models.BooleanField(null=True, blank=True)

	class Meta:
			db_table = 'works_mesh'
			managed = False

	def __str__(self):
			return f"MeSH for {self.work}: {self.descriptor_name}"
		

class WorksOpenAccess(models.Model):
	work = models.ForeignKey(
		Work,
		on_delete=models.DO_NOTHING,
		db_column = 'work_id',
		related_name = 'open_access'
	) 
	is_oa = models.BooleanField(null=True, blank=True)
	oa_status = models.TextField(null=True, blank=True)
	oa_url = models.TextField(null=True, blank=True)
	any_repository_has_fulltext = models.BooleanField(null=True, blank=True)

	class Meta:
			db_table = 'works_open_access'
			managed = False

	def __str__(self):
			return f"OA for {self.work}: {self.oa_status}"
		

class WorksPrimaryLocation(models.Model):
		work = models.ForeignKey(
			Work,
			on_delete=models.DO_NOTHING,
			db_column = 'work_id',
			related_name = 'primary_location'
		) 
		source= models.ForeignKey(
			Source,
			on_delete=models.DO_NOTHING,
			db_column = 'source_id',
			related_name = 'works_primary'
		) 
		landing_page_url = models.TextField(null=True, blank=True)
		pdf_url = models.TextField(null=True, blank=True)
		is_oa = models.BooleanField(null=True, blank=True)
		version = models.TextField(null=True, blank=True)
		license = models.TextField(null=True, blank=True)

		class Meta:
			db_table = 'works_primary_locations'
			managed = False

		def __str__(self):
			return f"Primary Location for {self.work}"
		

class WorksReferencedWork(models.Model):
		work = models.ForeignKey(
				Work,
				on_delete=models.DO_NOTHING,
				db_column = 'work_id',
				related_name = 'references'
		) 
		referenced_work = models.ForeignKey(
				Work,
				on_delete=models.DO_NOTHING,
				db_column = 'referenced_work_id',
				related_name = 'referenced_work_identifier'
		) 

		class Meta:
				db_table = 'works_referenced_works'
				managed = False

		def __str__(self):	
				return f"{self.work} references {self.referenced_work}"


class WorksRelatedWork(models.Model):
    work = models.ForeignKey(
        Work,
        on_delete=models.DO_NOTHING,
        db_column='work_id',
        related_name='related_works'
    )
    related_work = models.ForeignKey(
        Work,
        on_delete=models.DO_NOTHING,
        db_column='related_work_id',
        related_name='related_work_identifier'
    )

    class Meta:
        db_table = 'works_related_works'
        managed = False

    def __str__(self):
        return f"{self.work} related to {self.related_work}"


# VISTAS MATERIALIZADAS
class MvLatamAuthor(models.Model):
    id = models.TextField(primary_key=True)
    orcid = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    display_name_alternatives = SafeJSONField(blank=True, null=True)
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    last_known_institution = models.ForeignKey(
        Institution,
        on_delete=models.DO_NOTHING,
        db_column='last_known_institution',
        related_name='mv_latam_authors_last_known'
    )
    works_api_url = models.TextField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    country_code = models.TextField()
    institution_name = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'mv_latam_authors'

class MvIaConcept(models.Model):
	id = models.TextField(primary_key=True)
	display_name = models.TextField()
	level = models.IntegerField()
	description = models.TextField()
	works_count = models.IntegerField()
	cited_by_count = models.IntegerField() 

	class Meta:
		managed = False
		db_table = 'mv_ia_concepts'

class MvLatamIaAuthorConcept(models.Model):
    author_id = models.CharField(max_length=255, primary_key=True)
    display_name = models.CharField(max_length=500)
    concept_ids = ArrayField(models.CharField(max_length=255))
    concept_tfs = ArrayField(models.FloatField())
    
    class Meta:
        managed = False 
        db_table = 'mv_latam_ia_authors_concepts'
				

class MvIaCoauthorshipLatam(models.Model):
	coauthor_1 = models.CharField()
	coauthor_2 = models.CharField()
	shared_works = models.IntegerField()

	class Meta: 
		managed= False
		db_table = 'mv_ia_coauthorships_latam'

class MvIaCoauthorship(models.Model):
	coauthor_1 = models.CharField()
	coauthor_2 = models.CharField()
	shared_works = models.IntegerField()

	class Meta: 
		managed= False
		db_table = 'mv_ia_coauthorships'


class MvRecommendationAuthorPool(models.Model):
	author_id = models.CharField(primary_key=True)
	display_name = models.CharField()
	concept_ids = ArrayField(models.CharField(max_length=255))
	concept_tfs = ArrayField(models.BigIntegerField())

	class Meta:
		managed=False
		db_table = 'mv_recommendation_author_pool'
