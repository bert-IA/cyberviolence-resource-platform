
import { LinkButton } from "../ui/LinkButton";

const navItems = [
    { path: '/', label: 'Menu', icon: '🏠' },
    { path: '/configuration', label: 'Pays', icon: '🗺️' },
    { path: '/decouverte', label: 'Ressources', icon: '🔍' },
    { path: '/validation', label: 'Validation', icon: '✅' },
    { path: '/rag', label: 'RAG', icon: '🎯' },
]

export function Sidebar() {
    return (
        <aside className="w-64 bg-white border-r mt-2 border-gray-200 min-h-[calc(100vh-5rem)]">
            <nav className="p-4 space-y-2">
                {navItems.map((item) => (
                    <LinkButton
                        key={item.path}
                        to={item.path}
                        label={item.label}
                        icon={item.icon}
                        variant="sidebar"  // ← Nouveau variant
                    />
                ))}
            </nav>
        </aside>
    )
}