import { useState } from "react";
import { useResources } from "../hooks/useResources";
import { useRejectResource } from "../hooks/useRejectResource";
import { ResourceCard } from "../components/features/ResourceCard";
import { Button } from "../components/ui/Button";
import { type Resource } from "../services/api";
import { RagValidationModal } from "../components/features/RagValidationModal";
import { useValidateResource } from "../hooks/useValidateResource";
import { getLanguageName, getCountryName } from "../utils/formatters";
import { AddResourceModal } from "../components/features/AddResourceModal";


export function RagPage() {

    // états de selection de la langue puis du pays
    const [countryCode, setCountryCode] = useState<string | null>(null)
    const [languageCode, setLanguageCode] = useState<string | null>(null)

    //état de la ressource selectionnées
    const [selectedResource, setSelectedResource] = useState<Resource | null>(null)
    const [showAddModal, setShowAddModal] = useState(false)

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
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-3xl font-bold text-gray-900">📋 Validation RAG</h2>
                    <p className="text-gray-500 text-sm mt-1">{filtered.length} ressource(s) affichée(s) sur {resources.data?.length || 0}</p>
                </div>
                <Button
                    label="+ Ajout Manuel d'une ressource"
                    onClick={() => setShowAddModal(true)}
                    variant="secondary"
                />
            </div>

            {/* Toolbar filtres */}
            <div className="flex items-center gap-6 bg-gray-50 border border-gray-200 rounded-xl px-6 py-4 mb-6">
                <span className="text-base font-medium text-gray-500 shrink-0">Filtrer par</span>

                <div className="flex items-center gap-3">
                    <label className="text-base text-gray-600 shrink-0">🌐 Langue</label>
                    <select
                        value={languageCode ?? ''}
                        onChange={e => { setLanguageCode(e.target.value || null); setCountryCode(null) }}
                        className="border border-gray-300 rounded-lg px-4 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                        <option value="">Toutes</option>
                        {languages.map(lang => (
                            <option key={lang} value={lang}>{getLanguageName(lang)}</option>
                        ))}
                    </select>
                </div>

                <div className="w-px h-6 bg-gray-300" />

                <div className="flex items-center gap-3">
                    <label className="text-base text-gray-600 shrink-0">🌍 Pays</label>
                    <select
                        value={countryCode ?? ''}
                        onChange={e => setCountryCode(e.target.value || null)}
                        disabled={countries.length === 0}
                        className="border border-gray-300 rounded-lg px-4 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
                    >
                        <option value="">Tous</option>
                        {countries.map(code => (
                            <option key={code} value={code}>{getCountryName(code)}</option>
                        ))}
                    </select>
                </div>

                {(languageCode || countryCode) && (
                    <>
                        <div className="w-px h-6 bg-gray-300" />
                        <button
                            onClick={() => { setLanguageCode(null); setCountryCode(null) }}
                            className="text-base text-purple-600 hover:text-purple-800 font-medium"
                        >
                            Réinitialiser
                        </button>
                    </>
                )}
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
            {showAddModal && <AddResourceModal
                onClose={() => setShowAddModal(false)}
                onSucces={() => resources.refetch()}
            />}
        </div >
    )
}
