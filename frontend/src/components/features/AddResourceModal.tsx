import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchLanguagesConfig, enrichResource, createResource, type Resource } from "../../services/api";
import { Button } from "../ui/Button";


interface AddResourceModalProps {
    onClose: () => void
    onSucces: () => void
}

const CATEGORIES = [
    { value: 'service_support', label: "Service d'aide" },
    { value: 'procedure_plateforme', label: 'Procédure & Plateforme' },
    { value: 'signalement_autorite', label: 'Signalement & Autorité' },
]

// Noms lisibles pour les codes de langue (l'API retourne parfois des noms en caractères natifs)
const LANG_DISPLAY: Record<string, string> = {
    FR: 'Français', EN: 'English', ES: 'Español',
    IT: 'Italiano', DE: 'Deutsch', PT: 'Português',
    JA: 'Japonais', ZH: 'Chinois', AR: 'Arabe', RU: 'Russe',
    NL: 'Néerlandais', PL: 'Polonais', SV: 'Suédois',
}

function Field({ label, value }: { label: string; value?: string | boolean | null }) {
    if (value === undefined || value === null || value === '') return null
    const display = typeof value === 'boolean' ? (value ? 'Oui' : 'Non') : value
    return (
        <div>
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</span>
            <p className="text-sm text-gray-900 mt-0.5">{display}</p>
        </div>
    )
}

export function AddResourceModal({ onClose, onSucces }: AddResourceModalProps) {
    const [form, setForm] = useState({
        name: '',
        category: '',
        language: '',
        country_code: '',
        country_name: ''
    })

    const { data: config } = useQuery({
        queryKey: ['languages-config'],
        queryFn: fetchLanguagesConfig
    })

    const [step, setStep] = useState<'form' | 'preview'>('form')
    const [previewData, setPreviewData] = useState<Partial<Resource> | null>(null)

    const languages = Object.values(config?.languages ?? {})
    const filteredCountries = config?.languages[form.language]?.countries ?? []

    const handleChange = (field: string, value: string) => {
        setForm(prev => ({ ...prev, [field]: value }))
    }

    const handleLanguageChange = (lang: string) => {
        setForm(prev => ({ ...prev, language: lang, country_code: '', country_name: '' }))
    }

    const handleCountryChange = (countryCode: string) => {
        const country = filteredCountries.find(c => c.country_code === countryCode)
        if (!country) return
        setForm(prev => ({ ...prev, country_code: country.country_code, country_name: country.country_name }))
    }

    const enrichMutation = useMutation({ mutationFn: enrichResource })
    const createMutation = useMutation({ mutationFn: createResource })

    const isFormValid = !!(form.name && form.language && form.country_code && form.category)

    const handleSearch = async () => {
        const result = await enrichMutation.mutateAsync(form)
        setPreviewData(result)
        setStep('preview')
    }

    const handleConfirm = async () => {
        if (!previewData) return
        await createMutation.mutateAsync(previewData)
        onSucces()
        onClose()
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-white rounded-xl p-8 w-full max-w-3xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>

                {/* ── ÉTAPE 1 : Formulaire ── */}
                {step === 'form' && (
                    <div className="space-y-7">
                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-semibold text-gray-900">Ajouter une ressource</h2>
                            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
                        </div>

                        {/* Langue — pills */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-3">Langue</label>
                            <div className="flex flex-wrap gap-2">
                                {languages.map(lang => {
                                    const active = form.language === lang.code
                                    return (
                                        <button
                                            key={lang.code}
                                            type="button"
                                            onClick={() => handleLanguageChange(lang.code)}
                                            className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${active
                                                    ? 'bg-purple-600 text-white border-purple-600'
                                                    : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400 hover:text-purple-700'
                                                }`}
                                        >
                                            {LANG_DISPLAY[lang.code] ?? lang.code}
                                        </button>
                                    )
                                })}
                            </div>
                        </div>

                        {/* Pays — toujours présent, désactivé sans langue */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Pays</label>
                            <select
                                value={form.country_code}
                                onChange={(e) => handleCountryChange(e.target.value)}
                                disabled={!form.language}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                            >
                                <option value="">{form.language ? '-- Choisir un pays --' : '-- Choisir une langue d\'abord --'}</option>
                                {filteredCountries.map(item => (
                                    <option key={item.country_code} value={item.country_code}>
                                        {item.country_name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Nom */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Nom de l'organisation</label>
                            <input
                                value={form.name}
                                onChange={(e) => handleChange('name', e.target.value)}
                                placeholder="Ex : e-Enfance, Cybermalveillance.gouv.fr…"
                                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                            />
                        </div>

                        {/* Catégorie — pills */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-3">Catégorie</label>
                            <div className="flex flex-wrap gap-2">
                                {CATEGORIES.map(cat => {
                                    const active = form.category === cat.value
                                    return (
                                        <button
                                            key={cat.value}
                                            type="button"
                                            onClick={() => handleChange('category', cat.value)}
                                            className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${active
                                                    ? 'bg-purple-600 text-white border-purple-600'
                                                    : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400 hover:text-purple-700'
                                                }`}
                                        >
                                            {cat.label}
                                        </button>
                                    )
                                })}
                            </div>
                        </div>

                        {enrichMutation.isError && (
                            <p className="text-sm text-red-600">
                                Erreur : {enrichMutation.error instanceof Error ? enrichMutation.error.message : 'Une erreur est survenue'}
                            </p>
                        )}

                        <div className="flex justify-end gap-3 pt-2">
                            <Button label="Annuler" onClick={onClose} variant="secondary" />
                            <Button
                                label={enrichMutation.isPending ? "Recherche en cours…" : "Rechercher"}
                                onClick={handleSearch}
                                variant="primary"
                                disabled={!isFormValid || enrichMutation.isPending}
                            />
                        </div>
                    </div>
                )}

                {/* ── ÉTAPE 2 : Aperçu ── */}
                {step === 'preview' && previewData && (
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-semibold text-gray-900">Aperçu de la ressource</h2>
                            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
                        </div>
                        <p className="text-sm text-gray-500">Vérifiez les informations trouvées par le LLM avant de confirmer l'ajout.</p>

                        {/* Identité */}
                        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Identité</h3>
                            <Field label="Nom" value={previewData.organization_name} />
                            <Field label="Pays" value={previewData.country_name} />
                            <Field label="Langue" value={previewData.language} />
                            <Field label="Catégorie" value={CATEGORIES.find(c => c.value === previewData.category)?.label ?? previewData.category} />
                        </div>

                        {/* Liens */}
                        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Liens</h3>
                            {previewData.website && (
                                <div>
                                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Site web</span>
                                    <a href={previewData.website} target="_blank" rel="noreferrer" className="block text-sm text-blue-600 hover:underline mt-0.5 break-all">{previewData.website} ↗</a>
                                </div>
                            )}
                            {previewData.direct_link && (
                                <div>
                                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Lien direct</span>
                                    <a href={previewData.direct_link} target="_blank" rel="noreferrer" className="block text-sm text-blue-600 hover:underline mt-0.5 break-all">{previewData.direct_link} ↗</a>
                                </div>
                            )}
                        </div>

                        {/* Description */}
                        {previewData.description && (
                            <div className="bg-gray-50 rounded-lg p-4">
                                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Description</h3>
                                <p className="text-sm text-gray-900">{previewData.description}</p>
                            </div>
                        )}

                        {/* Contact */}
                        {previewData.phone && (
                            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Contact</h3>
                                <Field label="Téléphone" value={previewData.phone} />
                            </div>
                        )}

                        {/* Périmètre */}
                        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Périmètre</h3>
                            <Field label="Public visé" value={previewData.scope_audience} />
                            <Field label="Type de violence" value={previewData.scope_violence} />
                            <Field label="Signalement anonyme" value={previewData.scope_anonymous} />
                            <Field label="Source gouvernementale" value={previewData.is_governmental} />
                            <Field label="Type d'action" value={previewData.action_type} />
                            <Field label="Périmètre de signalement" value={previewData.scope_signalement} />
                        </div>

                        {createMutation.isError && (
                            <p className="text-sm text-red-600">
                                Erreur : {createMutation.error instanceof Error ? createMutation.error.message : 'Une erreur est survenue'}
                            </p>
                        )}

                        <div className="flex justify-end gap-3 pt-2">
                            <Button label="Recommencer" onClick={() => setStep('form')} variant="secondary" />
                            <Button
                                label={createMutation.isPending ? "Ajout en cours…" : "Confirmer l'ajout"}
                                onClick={handleConfirm}
                                variant="primary"
                                disabled={createMutation.isPending}
                            />
                        </div>
                    </div>
                )}

            </div>
        </div>
    )
}

