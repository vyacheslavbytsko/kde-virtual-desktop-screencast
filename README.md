# KDE virtual desktop screencast

Экспериментальная сборка v4 для Fedora 45 x86_64 и KDE Plasma 6.8.3 (Wayland). В системном диалоге демонстрации можно выбрать конкретный виртуальный рабочий стол и монитор. При локальном переключении поток продолжает показывать выбранный стол.

В v4 захватываются фон Plasma, окна и диалоги выбранного стола. Панель в кадре показывает значки открытых и свёрнутых окон этого стола. Настоящий курсор KWin передаётся по запросу приложения, пока выбранный стол активен на выбранном мониторе. Встроенная панель трансляции не включает виджеты штатной панели Plasma.

## Обновления Fedora 45 x86_64

GitHub Actions собирает `kwin`, `kwin-common`, `kwin-libs` и `xdg-desktop-portal-kde`, проверяет их совместную установку в отдельном контейнере и публикует подписанный репозиторий на [GitHub Pages](https://vyacheslavbytsko.github.io/kde-virtual-desktop-screencast/). Патч v4 применяется в обоих исходных пакетах, а общий XML-протокол встраивается при сборке. PipeWire и пакеты протоколов на ноутбуке обновляются обычным способом.

После первого успешного выпуска скачай `kde-virtual-desktop.repo` со страницы проекта и установи его командой `sudo dnf config-manager addrepo --from-repofile=./kde-virtual-desktop.repo`. При первом обновлении сверь отпечаток ключа с переменной `RPM_SIGNING_FINGERPRINT` в настройках Actions.

Исключи четыре пакета только из штатных репозиториев Fedora. Если списки исключений пустые, их можно задать так:

```bash
sudo dnf config-manager setopt \
  fedora.excludepkgs=kwin,kwin-common,kwin-libs,xdg-desktop-portal-kde \
  updates.excludepkgs=kwin,kwin-common,kwin-libs,xdg-desktop-portal-kde
```

Если уже есть исключения, дополни их. Если включён `updates-testing`, добавь эти имена и в него. Затем выполни `sudo dnf upgrade --refresh` и перезайди в сеанс Plasma.

### Выпуск новой сборки

Измени список исходных RPM и их хеши в `packaging/fedora/upstream-srpms.sha256`. Если изменилась версия Plasma, обнови патчи под неё. Для повторной публикации той же ревизии увеличь номер `--revision` в скрипте подготовки. GitHub Actions начнёт сборку после изменения в `main`. Также её можно запустить вручную во вкладке **Actions → Fedora 45 RPM repository**. При ошибке сборки или проверки установки Pages продолжит раздавать предыдущую версию.

Для публикации используются **Settings → Pages → GitHub Actions**, секрет Actions `RPM_SIGNING_KEY` с закрытым ключом OpenPGP и переменная Actions `RPM_SIGNING_FINGERPRINT` с его полным отпечатком. Проверка установки в контейнере подтверждает совместимость RPM. Сам захват виртуального стола проверяется в сеансе Plasma.

## Источники и лицензии

Патчи применяются к [KWin](https://invent.kde.org/plasma/kwin/-/tree/v6.8.3), [KDE Portal](https://invent.kde.org/plasma/xdg-desktop-portal-kde/-/tree/v6.8.3) и Wayland-протоколам Plasma версии 1.23.0. Изменения в исходных файлах распространяются на условиях лицензий этих файлов, указанных в их SPDX-заголовках. Соответствующие тексты лежат в `LICENSES/`.

Пакетные рецепты берутся из исходных RPM Fedora Koji, перечисленных в `packaging/fedora/upstream-srpms.sha256`. Скрипт сборки и тестовая HTML-страница доступны по GPL-2.0-or-later.
