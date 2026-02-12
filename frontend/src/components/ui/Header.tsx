
import { Button } from "./Button"

export interface NavigationItem<TPage> {
    label: string
    value: TPage
}

interface HeaderProps<TPage extends string> {
    title: string
    userName: string
    buttonLabel?: string
    onDemoClick?: () => void
    navigationItems?: NavigationItem<TPage>[]
    currentPage?: TPage
    onNavigate?: (page: TPage) => void
}

export function Header<TPage extends string>({
    title,
    userName,
    buttonLabel = 'Démo Tailwind',
    onDemoClick,
    navigationItems,
    currentPage,
    onNavigate
}: HeaderProps<TPage>) {

    return (
        <header className="bg-green-400 shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex justify-between items-center">
                    {/* Partie gauche : Titre + Navigation */}
                    <div className="flex flex-col gap-4">
                        <h1 className="text-3xl font-bold text-gray-900">
                            {title}
                        </h1>
                        {navigationItems && navigationItems.length > 0 && onNavigate && (
                            <nav className="flex gap-2">
                                {navigationItems.map((item) => (
                                    <Button
                                        key={item.value}
                                        label={item.label}
                                        onClick={() => onNavigate(item.value)}
                                        variant={currentPage === item.value ? 'tab-active' : 'tab'}
                                    />
                                ))}
                            </nav>
                        )}
                    </div>

                    {/* Partie droite : Bouton retour + User (centré verticalement) */}
                    <div className="flex items-center gap-2">
                        {onDemoClick && (
                            <Button
                                label={buttonLabel ?? '🎨 Démo Tailwind'}
                                onClick={onDemoClick}
                                variant='secondary'
                            />
                        )}
                        <span className="text-sm">👤</span>
                        <span>{userName}</span>
                    </div>
                </div>
            </div>
        </header>
    )
}



