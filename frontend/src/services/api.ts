export const API_BASE_URL = 'http://localhost:8000'
export const AUTH_TOKEN = 'Bearer admin-token-2024'

// Ressource complète (utilisée pour /sources, validation, etc.)
export interface Resource {
    id: string
    name: string
    title: string
    description: string
    url: string
    organization: string
    country: string
    region: string
    status: string
    contact_phone: string
    contact_email: string
    contact_url: string
    languages: string[]
    target_audience: string[]
    workflow_status: string
}

// Ressource découverte (structure simplifiée retournée par /geographic/discover)
export interface DiscoveredResource {
    id: string
    name: string
    country: string
    phone: string
    email: string
    confidence: number
    category: string
    description: string
    is_new: boolean
    duplicate_reason?: string
}

export interface DiscoveryFilters {
    language: string
    categories: string[]
    countries: string[]
    max_per_category: number
}

// Structure réelle retournée par le backend
interface BackendDiscoveryResponse {
    success: boolean
    message: string
    data: {
        discovered_count: number
        resources: DiscoveredResource[]
        estimated_duration?: string
        language: string
    }
}

// Structure adaptée pour le frontend
export interface DiscoveryResponse {
    success: boolean
    message: string
    total_discovered: number
    newly_discovered: DiscoveredResource[]
    estimated_duration?: string
}

// ============================================
// Fonctions API - Discovery
// ============================================

export async function discoverResources(
    filters: DiscoveryFilters
): Promise<DiscoveryResponse> {
    const response = await fetch(`${API_BASE_URL}/geographic/discover`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN
        },
        body: JSON.stringify(filters)
    })

    if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`)
    }

    const backendResponse: BackendDiscoveryResponse = await response.json()

    // Transformer la structure backend vers la structure frontend
    return {
        success: backendResponse.success,
        message: backendResponse.message,
        total_discovered: backendResponse.data.discovered_count,
        newly_discovered: backendResponse.data.resources,
        estimated_duration: backendResponse.data.estimated_duration
    }
}

// ============================================
// Fonctions API - Resources
// ============================================

export async function fetchResources(status?: string): Promise<Resource[]> {
    const url = status
        ? `${API_BASE_URL}/sources?status=${status}`
        : `${API_BASE_URL}/sources`

    const response = await fetch(url, {
        headers: { 'Authorization': AUTH_TOKEN }
    })

    if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`)
    }

    const data = await response.json()
    return data.sources || []
}

export async function fetchResourceById(id: string): Promise<Resource> {
    const response = await fetch(`${API_BASE_URL}/sources/${id}`, {
        headers: { 'Authorization': AUTH_TOKEN }
    })

    if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`)
    }

    const data = await response.json()
    return data.resource
}

// ============================================
// Fonctions API - Validation
// ============================================

export interface ValidateSourceRequest {
    source_id: string
    action: 'validate_critical' | 'reject'
    modifications?: Partial<Resource>
    criteria_checks?: Record<string, boolean>
    auto_transition_rag?: boolean
}

export async function validateCriticalSource(
    request: ValidateSourceRequest
): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/sources/validate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN
        },
        body: JSON.stringify(request)
    })

    if (!response.ok) {
        throw new Error(`Erreur validation: ${response.status}`)
    }

    return response.json()
}

// ============================================
// Fonctions API - Update & Extracted Data
// ============================================

export interface ExtractedContactData {
    phone?: string
    url?: string
    email?: string
    contact_type?: string
    availability?: string
}

export async function updateExtractedData(
    source_id: string,
    data: ExtractedContactData
): Promise<{ success: boolean; resource: Resource }> {
    const response = await fetch(`${API_BASE_URL}/sources/${source_id}/update-extracted-data`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN
        },
        body: JSON.stringify(data)
    })

    if (!response.ok) {
        throw new Error(`Erreur mise à jour: ${response.status}`)
    }

    return response.json()
}

export async function getExtractedData(
    source_id: string
): Promise<ExtractedContactData> {
    const response = await fetch(`${API_BASE_URL}/sources/${source_id}/extracted-data`, {
        headers: { 'Authorization': AUTH_TOKEN }
    })

    if (!response.ok) {
        throw new Error(`Erreur récupération: ${response.status}`)
    }

    const data = await response.json()
    return data.extracted_data
}