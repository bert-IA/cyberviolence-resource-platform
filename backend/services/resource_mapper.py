"""
Service de mapping des ressources : stockage JSON → contrat API V2

Une seule fonction map_resource_to_api() utilisée partout.
Si un champ change, on le corrige ici une fois.

Champs V2 exposés :
  organization_name, description
  country_name, country_code, language
  category, status, workflow_status
  website, direct_link, phone
  is_governmental
  scope_audience, scope_violence, scope_anonymous
  platform_name, action_type (procedure_plateforme)
"""

from typing import Dict, Any


def map_resource_to_api(resource_id: str, resource_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mappe les données brutes du stockage JSON vers le contrat API frontend.

    Règle : on ne lit qu'ici les noms des champs JSON.
    Si working_resources.json change, on n'a qu'un seul endroit à modifier.

    Args:
        resource_id   : clé primaire de la ressource (ex: DISCOVERED_FR_...)
        resource_data : dictionnaire brut issu de working_resources.json

    Returns:
        Dictionnaire normalisé conforme à l'interface TypeScript Resource
    """
    metadata = resource_data.get("metadata", {})

    return {
        # --- Identité ---
        "id":                resource_id,
        # "name" = clé interne Python → "organization_name" = clé publique API
        "organization_name": resource_data.get("name", ""),
        "description":       resource_data.get("description", ""),

        # --- Géographie ---
        "country_name":      resource_data.get("country_name", ""),
        "country_code":      resource_data.get("country_code", ""),

        # --- Catégorie ---
        "category":          metadata.get("category", resource_data.get("category", "")),

        # --- Workflow ---
        "status":            resource_data.get("workflow_status", ""),
        "workflow_status":   resource_data.get("workflow_status", ""),

        # --- Contact ---
        "website":           resource_data.get("website", ""),
        "direct_link":       resource_data.get("direct_link", ""),
        "phone":             resource_data.get("phone", ""),

        # --- Gouvernance ---
        "is_governmental":   resource_data.get("is_governmental", False),

        # --- Périmètre ---
        "scope_audience":    resource_data.get("scope_audience",  metadata.get("scope_audience", "")),
        "scope_violence":    resource_data.get("scope_violence",  metadata.get("scope_violence", "")),
        "scope_anonymous":   resource_data.get("scope_anonymous", metadata.get("scope_anonymous", False)),

        # --- Champs spécifiques procedure_plateforme ---
        "action_type":       resource_data.get("action_type",   metadata.get("action_type", "")),

        # --- Champs spécifiques signalement_autorite ---
        "scope_signalement": resource_data.get("scope_signalement", metadata.get("scope_signalement", "")),

        # --- Langue ---
        "language":          resource_data.get("language", ""),

        # --- Statut nouveauté ---
        "is_new":            resource_data.get("is_new", None),

        # --- Métadonnées internes ---
        "metadata":          metadata,
    }


def map_resources_list(resources: Dict[str, Any]) -> list:
    """
    Mappe un dictionnaire de ressources {id: data} en liste d'objets API.
    Utilisé par GET /sources et GET /sources/summary.

    Args:
        resources : dictionnaire {resource_id: resource_data}

    Returns:
        Liste de ressources normalisées
    """
    return [
        map_resource_to_api(resource_id, resource_data)
        for resource_id, resource_data in resources.items()
    ]
