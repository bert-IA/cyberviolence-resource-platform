import { useState } from 'react'


interface ExpandableTextProps {
    text: string
    maxLength?: number
    className?: string
}

export function ExpandableText({
    text,
    maxLength = 150,
    className = ''
}: ExpandableTextProps) {
    // 1️⃣ État local : commence tronqué
    const [isExpanded, setIsExpanded] = useState(false)

    // 2️⃣ Condition : afficher bouton seulement si texte > maxLength
    const shouldShowButton = text.length > maxLength

    // 3️⃣ Logique d'affichage du texte
    const displayText = (isExpanded || !shouldShowButton)
        ? text  // Texte complet
        : text.substring(0, maxLength) + '...'  // Texte tronqué

    // 4️⃣ Toggle expand/collapse
    const handleToggle = () => {
        setIsExpanded(!isExpanded)
    }

    return (
        <div className={className}>
            {/* Texte affiché */}
            <span className="text-gray-600 text-sm mb-2">
                {displayText}
            </span>
            {'  '}

            {/* Bouton conditionnel */}
            {shouldShowButton && (
                <button
                    onClick={handleToggle}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
                >
                    {isExpanded ? 'Lire moins' : 'Lire plus'}
                </button>
            )}
        </div>
    )
}