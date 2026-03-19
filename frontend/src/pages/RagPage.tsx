import { useState } from "react";
import { useResources } from "../hooks/useResources";
import { useRejectResource } from "../hooks/useRejectResource";
import { ResourceCard } from "../components/features/ResourceCard";
import { Button } from "../components/ui/Button";
import { type Resource } from "../services/api";
import { RagValidationModal } from "../components/features/RagValidationModal";
import { useValidateResource } from "../hooks/useValidateResource";
import { getLanguageName, getCountryName } from "../utils/formatters";


export function RagPage() {

    // états de selection de la langue puis du pays
    const [countryCode, setCountryCode] = useState<string | null>(null)
    const [languageCode, setLanguageCode] = useState<string | null>(null)

    //état de la ressource selectionnées
    const [selectedResource, setSelectedResource] = useState<Resource | null>(null)

    // récupération des  ressources à valider pour le RAG
    const resources = useResources('critical_pending')

    // filtrage par langue et récupération des langues présentes dans les ressources
    const filteredLanguage = resources.data?.filter(r => languageCode === null ||
        r.language === languageCode) ?? []

    // récupération des langues des ressources 
    const languages = [... new Set(resources.data?.map(r => r.language)) ?? []]

    // filtrage par pays une fois la langue choisie
    const filtered = filteredLanguage?.filter(r => countryCode === null ||
        r.country_code === countryCode) ?? []

    const countries = [...new Set(filteredLanguage?.map(r => r.country_code) ?? [])]

    //fonction de rejet des resources
    const rejectMutation = useRejectResource()

    const handleRejectResource = (id: string) => {
        rejectMutation.mutate(id, {
            onSuccess: () => {
                resources.refetch()
                setSelectedResource(null)
            }
        })
    }

    const validateMutation = useValidateResource()
    const handleValidateResource = (id: string) => {
        validateMutation.mutate(id, {
            onSuccess: () => {
                resources.refetch()
                setSelectedResource(null)
            }
        })
    }

    if (resources.isLoading) {
        return (
            <div className="p-6">
                <div className="text-center py-16">
                    <div className="text-2xl">⏳</div>
                    <p className="text-gray-600 mt-2">Chargement des ressources...</p>
                </div>
            </div>
        )
    }

    // État : Erreur
    if (resources.error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800 font-medium">❌ Erreur de chargement</p>
                    <p className="text-red-600 text-sm mt-1">{resources.error.message}</p>
                </div>
            </div>
        )
    }

    return (
        <div className="p-6">
            {/* En-tête */}
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    📋 Ressources en attente de validation RAG
                </h2>
                <p className="text-gray-600">
                    {resources.data?.length || 0} ressource(s) à traiter
                </p>
            </div>
            {/* Zone 0 — boutons filtre langue */}
            <div className="mb-4">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">🌐 Filtrer par langue</h3>
                <div className="flex gap-2 flex-wrap">
                    <Button
                        label={`Toutes (${resources.data?.length || 0})`}
                        onClick={() => setLanguageCode(null)}
                        variant={languageCode === null ? 'tab-active' : 'tab'}
                    />
                    {languages.map(lang => (
                        <Button
                            key={lang}
                            label={`${getLanguageName(lang)} (${resources.data?.filter(r => r.language === lang).length ?? 0})`}
                            onClick={() => setLanguageCode(lang)}
                            variant={languageCode === lang ? 'tab-active' : 'tab'}
                        />
                    ))}
                </div>
            </div>

            {/* Zone 1 — boutons filtre pays */}
            <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">🌍 Filtrer par pays</h3>
                <div className="flex gap-2 flex-wrap">
                    <Button
                        label={`Tous (${filteredLanguage.length})`}
                        onClick={() => setCountryCode(null)}
                        variant={countryCode === null ? 'tab-active' : 'tab'}
                    />
                    {countries.map(code => (
                        <Button
                            key={code}
                            label={`${getCountryName(code)} (${filteredLanguage.filter(r => r.country_code === code).length})`}
                            onClick={() => setCountryCode(code)}
                            variant={countryCode === code ? 'tab-active' : 'tab'}
                        />
                    ))}
                </div>
            </div>

            {/* Zone 2 — liste des ressources */}
            {
                filtered.length === 0 ? (
                    <div className="text-center py-16 text-gray-400">
                        <div className="text-4xl mb-3">✅</div>
                        <p className="text-lg font-medium">Aucune ressource à valider</p>
                        <p className="text-sm mt-1">Toutes les ressources ont été traitées pour cette sélection.</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {filtered.map(resource => (
                            <ResourceCard key={resource.id} resource={resource}>
                                {/* boutons Rejeter et Voir détails */}
                                <Button
                                    label="Rejeter"
                                    onClick={() => handleRejectResource(resource.id)}
                                    variant="danger"
                                />
                                <Button
                                    label="Voir détails"
                                    onClick={() => setSelectedResource(resource)}
                                    variant="secondary"
                                />
                            </ResourceCard>
                        ))}
                    </div>

                )
            }
            {
                selectedResource && <RagValidationModal
                    resource={selectedResource}
                    onClose={() => setSelectedResource(null)}
                    onReject={handleRejectResource}
                    onValidate={handleValidateResource} />
            }
        </div >
    )
}
