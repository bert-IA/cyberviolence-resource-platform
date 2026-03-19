export function getLanguageName(code: string): string {
    return new Intl.DisplayNames(['fr'], { type: 'language' }).of(code) ?? code
}

export function getCountryName(code: string): string {
    try {
        return new Intl.DisplayNames(['fr'], { type: 'region' }).of(code) ?? code
    } catch {
        return code
    }
}

export function getFlagEmoji(code: string): string {
    return code.toUpperCase().split('')
        .map(c => String.fromCodePoint(127397 + c.charCodeAt(0)))
        .join('')
}