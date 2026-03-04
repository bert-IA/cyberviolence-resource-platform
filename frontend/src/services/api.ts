export const API_BASE_URL = 'http://localhost:8000'
export const AUTH_TOKEN = 'Bearer admin-token-2024'

// Ressource complète (utilisée pour /sources, validation, etc.)
// === INTERFACES ===

interface BaseResource {
    id: string
    organization_name: string
    website: string
    direct_link: string
    description: string
    category: string
    scope_audience?: string
    scope_violence?: string
    scope_anonymous: boolean
    is_governmental?: boolean
    country_name: string
    country_code: string
    language: string
    phone?: string
}

export interface Resource extends BaseResource {
    status: string
    workflow_status: string
    is_new?: boolean | null
    scope_signalement?: string
    action_type?: string
}

export interface DiscoveredResource extends BaseResource {
    confidence: number
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
export interface ValidationRequest {
    resource_ids: string[]  // ✅ FIX: Aligné avec le backend (était source_ids)
    action: 'approve' | 'reject'
}

export interface ValidationResponse {
    approved: number
    rejected: number
    message: string
}

// 🆕 Interface pour les stats groupées
export interface ResourceStats {
    success: boolean
    status_filtered: string  // 🆕 Statut filtré (discovered, geo_validated, rag_ready)
    total_pending: number
    by_country: {
        [countryCode: string]: {
            count: number
            label: string
        }
    }
    by_category: {
        [category: string]: number
    }
}

export interface CountryConfig {
    country_name: string
    country_code: string
    flag: string
}

export interface LanguageConfig {
    countries: CountryConfig[]

}

export interface ConfigResponse {
    success: boolean
    languages: { [langageCode: string]: LanguageConfig }
}

// ============================================
// Fonctions API - ConfigLanguage
// ============================================
export async function fetchLanguagesConfig(): Promise<ConfigResponse> {
    const response = await fetch(`${API_BASE_URL}/admin/config/countries-languages`, {
        headers: { 'Authorization': AUTH_TOKEN }
    })
    if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`)
    }

    return response.json()
}



// ============================================
// Fonctions API - Discovery
// ============================================

export async function discoverResources(
    filters: DiscoveryFilters
): Promise<DiscoveryResponse> {
    console.log('📤 [API] POST /geographic/discover avec:', JSON.stringify(filters, null, 2))

    const response = await fetch(`${API_BASE_URL}/geographic/discover`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN
        },
        body: JSON.stringify(filters)
    })

    console.log('📥 [API] Response status:', response.status, response.statusText)

    if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ [API] Erreur response:', errorText)
        throw new Error(`Erreur API: ${response.status}`)
    }

    const backendResponse: BackendDiscoveryResponse = await response.json()
    console.log('📦 [API] Backend response:', JSON.stringify(backendResponse, null, 2))

    // Transformer la structure backend vers la structure frontend
    const result = {
        success: backendResponse.success,
        message: backendResponse.message,
        total_discovered: backendResponse.data.discovered_count,
        newly_discovered: backendResponse.data.resources,
        estimated_duration: backendResponse.data.estimated_duration
    }

    console.log('🔄 [API] Transformation frontend:', result)
    return result
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

export async function validateResource(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/sources/${id}/validate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN
        }
    })

    if (!response.ok) {
        throw new Error(`Erreur validation: ${response.status}`)
    }
}

export async function rejectResource(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/sources/${id}/reject`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN
        }
    })

    if (!response.ok) {
        throw new Error(`Erreur rejet: ${response.status}`)
    }
}
export async function validateBatch(
    request: ValidationRequest
): Promise<ValidationResponse> {
    const response = await fetch(`${API_BASE_URL}/geographic/validate-batch`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN,
        },
        body: JSON.stringify(request),
    })

    if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`)
    }

    return response.json()
}

// 🆕 FONCTION STATS GROUPÉES

export async function getResourceStats(
    status: string = 'discovered'  // 🆕 Paramètre status avec valeur par défaut
): Promise<ResourceStats> {
    const response = await fetch(`${API_BASE_URL}/sources/summary?status=${status}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN,
        },
    })

    if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.statusText}`)
    }

    return response.json()
}

// ============================================
// Fonctions API - Update
// ============================================

export async function updateResource(
    id: string,
    data: Partial<Resource>
): Promise<Resource> {
    const response = await fetch(`${API_BASE_URL}/sources/${id}`, {
        method: 'PATCH',
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