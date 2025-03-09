"""
Pydantic models for Jira boards and related objects.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict


class BoardLocation(BaseModel):
    """Lokalizacja tablicy."""
    project_id: Optional[int] = Field(None, description="ID projektu", alias="projectId")
    project_key: Optional[str] = Field(None, description="Klucz projektu", alias="projectKey")
    project_name: Optional[str] = Field(None, description="Nazwa projektu", alias="projectName")
    display_name: Optional[str] = Field(None, description="Wyświetlana nazwa", alias="displayName")
    
    model_config = ConfigDict(populate_by_name=True)


class BoardColumnStatus(BaseModel):
    """Status kolumny tablicy."""
    id: str = Field(..., description="ID statusu")
    name: str = Field(..., description="Nazwa statusu")


class BoardColumn(BaseModel):
    """Kolumna tablicy."""
    id: int = Field(..., description="ID kolumny")
    name: str = Field(..., description="Nazwa kolumny")
    statuses: List[BoardColumnStatus] = Field([], description="Statusy kolumny")


class BoardConfiguration(BaseModel):
    """Konfiguracja tablicy."""
    id: int = Field(..., description="ID konfiguracji")
    name: str = Field(..., description="Nazwa konfiguracji")
    columns_config: Dict[str, Any] = Field(..., description="Konfiguracja kolumn", alias="columnsConfig")
    ranking_config: Optional[Dict[str, Any]] = Field(None, description="Konfiguracja rankingu", alias="rankingConfig")
    swimlanes_config: Optional[Dict[str, Any]] = Field(None, description="Konfiguracja swimlane'ów", alias="swimlanesConfig")
    estimation_config: Optional[Dict[str, Any]] = Field(None, description="Konfiguracja szacowania", alias="estimationConfig")
    
    model_config = ConfigDict(populate_by_name=True)


class QuickFilter(BaseModel):
    """Szybki filtr tablicy."""
    id: int = Field(..., description="ID filtra")
    name: str = Field(..., description="Nazwa filtra")
    jql: str = Field(..., description="Zapytanie JQL filtra")
    description: Optional[str] = Field(None, description="Opis filtra")
    icon_uri: Optional[str] = Field(None, description="URI ikony filtra", alias="iconUri")
    position: Optional[int] = Field(None, description="Pozycja filtra")
    
    model_config = ConfigDict(populate_by_name=True)


class BoardReference(BaseModel):
    """Referencja do tablicy."""
    id: int = Field(..., description="ID tablicy")
    name: str = Field(..., description="Nazwa tablicy")
    type: str = Field(..., description="Typ tablicy")
    location: Optional[BoardLocation] = Field(None, description="Lokalizacja tablicy")
    
    model_config = ConfigDict(populate_by_name=True)


class BoardCreate(BaseModel):
    """Dane potrzebne do utworzenia tablicy."""
    name: str = Field(..., description="Nazwa tablicy")
    type: str = Field(..., description="Typ tablicy")
    filter_id: int = Field(..., description="ID filtra", alias="filterId")
    location: Optional[Dict[str, Any]] = Field(None, description="Lokalizacja tablicy")
    
    model_config = ConfigDict(populate_by_name=True)


class BoardUpdate(BaseModel):
    """Dane potrzebne do aktualizacji tablicy."""
    name: Optional[str] = Field(None, description="Nowa nazwa tablicy")
    filter_id: Optional[int] = Field(None, description="Nowy ID filtra", alias="filterId")
    
    model_config = ConfigDict(populate_by_name=True)


class Board(BaseModel):
    """Pełne dane tablicy."""
    id: int = Field(..., description="ID tablicy")
    name: str = Field(..., description="Nazwa tablicy")
    type: str = Field(..., description="Typ tablicy")
    location: Optional[BoardLocation] = Field(None, description="Lokalizacja tablicy")
    filter_id: int = Field(..., description="ID filtra", alias="filterId")
    configuration: Optional[BoardConfiguration] = Field(None, description="Konfiguracja tablicy")
    
    model_config = ConfigDict(populate_by_name=True)
