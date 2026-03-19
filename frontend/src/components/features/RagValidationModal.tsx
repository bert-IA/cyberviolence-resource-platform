import { useState } from "react";
import { usePatchResource } from '../../hooks/usePatchResource'
import { type Resource } from "../../services/api";
import { Button } from "../ui/Button";

interface RagValidationModalProps {
    resource: Resource
    onClose: () => void
    onValidate: (id: string) => void
    onReject: (id: string) => void
}

export function RagValidationModal({
    resource,
    onClose,
    onValidate,
    onReject }: RagValidationModalProps) {


    const [form, setForm] = useState({
        organization_name: resource.organization_name,
        description: resource.description ?? '',
        website: resource.website ?? '',
        direct_link: resource.direct_link ?? '',
        phone: resource.phone ?? '',
    })

    const handleChange = (field: string, value: string) => {
        setForm(prev => ({ ...prev, [field]: value }))
    }
    const patchMutation = usePatchResource()

    const handleValidate = async () => {
        await patchMutation.mutateAsync({ id: resource.id, data: form })
        onValidate(resource.id)
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" >
            <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                {/* En-tête */}
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold text-gray-900">{resource.organization_name}</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">✕</button>
                </div>

                <div className="space-y-4 mb-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Nom de l'organisation</label>
                        <input
                            value={form.organization_name}
                            onChange={(e) => handleChange('organization_name', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea
                            value={form.description}
                            onChange={(e) => handleChange('description', e.target.value)}
                            rows={4}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                        <input
                            value={form.website}
                            onChange={(e) => handleChange('website', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                        {form.website && (
                            <a href={form.website} target="_blank" rel="noreferrer" className="text-xs text-blue-500 hover:underline mt-1 block">
                                Ouvrir le lien ↗
                            </a>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Lien direct</label>
                        <input
                            value={form.direct_link}
                            onChange={(e) => handleChange('direct_link', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                        {form.direct_link && (
                            <a href={form.direct_link} target="_blank" rel="noreferrer" className="text-xs text-blue-500 hover:underline mt-1 block">
                                Ouvrir le lien ↗
                            </a>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
                        <input
                            value={form.phone}
                            onChange={(e) => handleChange('phone', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                    </div>
                </div>

                {/* Périmètre — lecture seule */}
                <div className="bg-gray-50 rounded-lg p-4 space-y-3 mb-6">
                    <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Périmètre</h3>
                    <div className="grid grid-cols-2 gap-3">
                        {resource.scope_audience && (
                            <div>
                                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Public visé</span>
                                <p className="text-sm text-gray-900 mt-0.5">{resource.scope_audience}</p>
                            </div>
                        )}
                        {resource.scope_violence && (
                            <div>
                                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Type de violence</span>
                                <p className="text-sm text-gray-900 mt-0.5">{resource.scope_violence}</p>
                            </div>
                        )}
                        {resource.action_type && (
                            <div>
                                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Type d'action</span>
                                <p className="text-sm text-gray-900 mt-0.5">{resource.action_type}</p>
                            </div>
                        )}
                        {resource.scope_signalement && (
                            <div>
                                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Périmètre signalement</span>
                                <p className="text-sm text-gray-900 mt-0.5">{resource.scope_signalement}</p>
                            </div>
                        )}
                        <div>
                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Anonyme</span>
                            <p className="text-sm text-gray-900 mt-0.5">{resource.scope_anonymous ? 'Oui' : 'Non'}</p>
                        </div>
                        {resource.is_governmental !== undefined && resource.is_governmental !== null && (
                            <div>
                                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Gouvernemental</span>
                                <p className="text-sm text-gray-900 mt-0.5">{resource.is_governmental ? 'Oui' : 'Non'}</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t">
                    <Button
                        label="Rejeter"
                        onClick={() => onReject(resource.id)}
                        variant="danger"
                    />
                    <Button
                        label="Valider"
                        onClick={() => handleValidate()}
                        variant="primary"
                    />
                    <Button
                        label="Annuler"
                        onClick={onClose}
                        variant="secondary" />
                </div>

            </div>

        </div>
    )
}