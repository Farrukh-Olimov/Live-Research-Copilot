from .author_repository import AuthorRespotitory
from .datasource_repository import DatasourceRepository
from .domain_repository import DomainRepository
from .paper_repository import PaperRepository
from .paper_subject_repository import PaperSubjectRepository
from .subject_repository import SubjectRepository

__all__ = [
    "AuthorRespotitory",
    "DatasourceRepository",
    "DomainRepository",
    "PaperRepository",
    "PaperSubjectRepository",
    "SubjectRepository",
]


class DatabaseRepository:
    def __init__(self):
        self.author = AuthorRespotitory()
        self.datasource = DatasourceRepository()
        self.domain = DomainRepository()
        self.paper = PaperRepository()
        self.paper_subject = PaperSubjectRepository()
        self.subject = SubjectRepository()
