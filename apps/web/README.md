# GrowthPilot web application

Bu dizin Next.js tabanlı GrowthPilot yönetim arayüzüdür. Tarayıcıya credential göndermez;
API erişimi yalnız Next.js sunucusundaki `GP_API_URL`, `GP_SERVER_TOKEN` ve
`GP_ORGANIZATION_ID` değişkenleri üzerinden yapılır.

## Temel yapı

- `src/app/`: route ve layout'lar
- `src/components/`: uygulama kabuğu ve yeniden kullanılabilir UI parçaları
- `src/lib/api.ts`: server-only API sınırı
- `src/lib/presentation.ts`: dürüst UI durum/presentation kuralları
- `e2e/`: 13 ana route için desktop/mobile Playwright ve Axe kontrolleri

Backend ulaşılamıyorsa veya ortam değişkenleri yoksa arayüz sahte sayı üretmez; açık bir
`unconfigured` ya da `error` durumu gösterir.

## Komutlar

Repository kökünden:

```sh
pnpm dev
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm test:e2e
```

E2E öncesi Chromium gerekirse bir kez
`pnpm --filter @growthpilot/web exec playwright install chromium` çalıştırın. Tam yerel
kurulum için [`docs/LOCAL_DEVELOPMENT.md`](../../docs/LOCAL_DEVELOPMENT.md).
