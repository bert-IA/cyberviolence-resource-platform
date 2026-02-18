interface ButtonProps {
    label: string
    onClick: () => void
    variant?: 'primary' | 'secondary' | 'tab' | 'tab-active'
    disabled?: boolean
    type?: 'button' | 'submit' | 'reset'
}

export function Button({
    label,
    onClick,
    variant = 'primary',
    disabled = false,
    type = 'button'

}: ButtonProps) {

    const baseStyles = "px-4 py-2 rounded-lg font-medium transition-colors"

    const variantStyles = {
        primary: "bg-green-500 text-gray-700 hover:bg-purple-600",
        secondary: "bg-blue-400 text-gray-700 hover:bg-green-600",
        tab: "bg-purple-300 text-gray-700 hover:bg-gray-200",
        'tab-active': "bg-purple-600 text-white"
    }[variant]

    const disabledStyles = disabled
        ? "opacity-50 cursor-not-allowed"
        : "cursor-pointer"

    return (
        <button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={`${baseStyles} ${variantStyles} ${disabledStyles}`}
        >
            {label}
        </button>
    )
}

