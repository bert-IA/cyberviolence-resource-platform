interface ButtonProps {
    label: string
    onClick: () => void
    variant?: 'primary' | 'secondary' | 'tab' | 'tab-active'
    disabled?: boolean
    type?: 'button' | 'submit' | 'reset'  // ← Ajouter cette ligne
}

export function Button({
    label,
    onClick,
    variant = 'primary',
    disabled = false,
    type = 'button'  // ← Ajouter ce param avec valeur par défaut
}: ButtonProps) {

    const baseStyles = "px-4 py-2 rounded-lg font-medium transition-colors"

    const variantStyles = {
        primary: "bg-green-500 text-white hover:bg-purple-600",
        secondary: "bg-blue-400 text-gray-700 hover:bg-green-600",
        tab: "bg-purple-300 text-gray-700 hover:bg-gray-200",
        'tab-active': "bg-purple-600 text-white"
    }[variant]

    const disabledStyles = disabled
        ? "opacity-50 cursor-not-allowed"
        : "cursor-pointer"

    return (
        <button
            type={type}  // ← Ajouter cette ligne
            onClick={onClick}
            disabled={disabled}
            className={`${baseStyles} ${variantStyles} ${disabledStyles}`}
        >
            {label}
        </button>
    )
}

