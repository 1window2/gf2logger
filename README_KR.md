# macOS용 gfl2logger

[English](README.md) | 한국어

> [!IMPORTANT]
> 이 리포지토리는 [blead/gfl2logger](https://github.com/blead/gfl2logger)의 macOS 전용 포크입니다.
> Windows 사용자는 [원본 Windows 버전](https://github.com/blead/gfl2logger/releases)을 다운로드하여 사용해야 합니다.

`gfl2logger`는 소녀전선 2: 망명(Girls' Frontline 2: Exilium)의 네트워크 페이로드를 캡처하고 서클 관리 데이터를 로컬 CSV 및 JSON 파일로 내보냅니다.
이 포크는 Apple Silicon Mac에서 실행되는 iPhone/iPad App Store 버전의 GF2를 지원합니다.

## 안내

> [!WARNING]
> `gf2logger`는 현재 임시 서명되어 있으며 아직 Apple Developer ID로 공증되지 않았기 때문에, 처음 실행할 때 macOS에서 Apple이 앱에 악성 소프트웨어가 없는지 확인할 수 없다는 **“gf2logger”이(가) 열리지 않음** 경고가 표시될 수 있습니다.
> 이 저장소의 [공식 Releases 페이지](https://github.com/1window2/gf2logger/releases)에서 앱을 다운로드했고 해당 출처를 신뢰하는 경우에만 이 경고를 우회하십시오.
>
> 앱 실행을 허용하는 방법은 다음과 같습니다.
>
> 1. `gf2logger.app`을 열어 본 다음 경고가 나타나면 **완료**를 클릭합니다.
> 2. **Apple 메뉴 > 시스템 설정 > 개인정보 보호 및 보안**을 엽니다.
> 3. **보안**까지 아래로 스크롤하고 `gf2logger`가 차단되었다는 메시지를 찾은 다음 **그래도 열기**를 클릭합니다.
> 4. 로그인 암호 또는 Touch ID로 인증한 다음, macOS에서 다시 확인을 요청하면 **열기**를 클릭합니다.
>
> **그래도 열기** 버튼은 차단된 실행을 시도한 후 약 1시간 동안 사용할 수 있습니다.
> 승인하면 macOS가 이 앱을 예외로 저장하므로 이후에는 정상적으로 실행할 수 있습니다.
> 자세한 내용은 [Apple 공식 안내](https://support.apple.com/ko-kr/guide/mac-help/mchleab3a043/mac)를 참조하십시오.

## 요구 사항

- Apple Silicon Mac
- Mac App Store에서 설치한 iPhone/iPad 버전의 `소녀전선 2: 망명`
- 번들로 제공되는 Mitmproxy Redirector 네트워크 확장 프로그램을 활성화할 권한

## 설치

1. [Releases](https://github.com/1window2/gf2logger/releases)에서
   `gf2logger-v0.1.1-macos-arm64.zip` 또는 `gf2logger-v0.1.1-macos-arm64.dmg`를 다운로드합니다.
2. ZIP의 경우 압축을 푼 다음 `gf2logger.app`을 Control-클릭합니다.
   DMG의 경우 파일을 열고 `gf2logger.app`을 **응용 프로그램**으로 드래그한 다음, 설치된 앱을 Control-클릭합니다.
3. **열기**를 선택한 다음 Gatekeeper 대화상자에서 **열기**를 다시 확인합니다.
4. macOS에서 네트워크 확장 프로그램 권한을 요청하면 **Mitmproxy Redirector**를 승인합니다.

Redirector가 자동으로 활성화되지 않으면 **시스템 설정 > 일반 > 로그인 항목 및 확장 프로그램 > 네트워크 확장 프로그램**을 열고,
**Mitmproxy Redirector**를 활성화한 다음 `gfl2logger`를 다시 실행합니다.

애플리케이션 자체는 현재 Developer ID로 서명 및 공증된 상태가 아니라 임시(ad-hoc) 서명된 상태입니다.
번들로 제공되는 네트워크 Redirector는 mitmproxy 프로젝트에서 별도로 서명하고 공증했습니다.

## 사용법

1. GF2보다 먼저 `gfl2logger`를 실행합니다. GF2가 이미 실행 중이라면 로거가
   준비된 후 GF2를 다시 시작합니다.
2. 원하는 페이로드 체크박스를 활성화된 상태로 둡니다.
3. GF2를 실행하고 서클 페이지를 열어 관련 데이터를 요청합니다.

내보낸 파일과 `gfl2logger.config.yaml`은 `~/gfl2logger`에 저장됩니다.

체크박스는 두 그룹으로 구성됩니다.

- **Platoon:** Platoon Profile, Members, Activity, Updates
- **Others:** Weapons, Attachments, Common Keys, Formations

### 내보내는 데이터

| 옵션 | 페이로드 | 설명 | 형식 |
| --- | ---: | --- | --- |
| Platoon Profile | `21905` | 서클 식별 정보, 레벨, 멤버 수, 공지 및 모집 안내 | JSON |
| Members | `21917` | 멤버 이름, UID, 레벨, 공적치, 점수 및 로그인 시간 | CSV |
| Activity | `21935` | 서클 목표 및 최근 멤버 활동 | JSON |
| Updates | `21960` | 동향 탭의 멤버 가입/탈퇴/추방 및 과업 보급 생성 기록 | JSON |
| Weapons | `11021` | 현재 계정이 보유한 무기 | CSV |
| Attachments | `11061` | 현재 계정이 보유한 파츠 | CSV |
| Common Keys | `11138` | 현재 계정이 보유한 공용키 | CSV |
| Formations | `23201` | 저장된 편성 | JSON |

## 작동 방식

Mitmproxy의 로컬 캡처 모드는 가로채기 대상을 GF2 실행 파일인 `SnqxExilium`으로 제한합니다.
로거는 게임 연결을 시작하거나 수정하지 않고 서버에서 클라이언트로 전송되는 페이로드를 읽습니다.
TLS 연결은 복호화하지 않고 그대로 통과시키므로 mitmproxy 인증서를 설치할 필요가 없습니다.

## 소스에서 빌드하기

이 프로젝트는 [PDM](https://pdm-project.org/)과 Python 3.13을 사용합니다.

```sh
git clone https://github.com/1window2/gf2logger.git
cd gf2logger
pdm install
pdm run pyinstaller
```

Apple Silicon 빌드는 `dist/gf2logger.app`에 생성됩니다. 소스에서 직접
실행하려면 다음 명령을 사용합니다.

```sh
pdm run protoc
pdm run python main.py
```

## 크레딧

패킷 파서, 데이터 내보내기 기능 및 원본 Windows 애플리케이션은
[blead](https://github.com/blead)가 [blead/gfl2logger](https://github.com/blead/gfl2logger)에서 제작했습니다.
이 포크는 macOS 캡처 경로, 패키징, 플랫폼별 UI 수정 및 확장된 서클 페이로드 지원을 추가합니다.

## 라이선스

이 프로젝트는 원본 MIT 라이선스를 유지합니다. [LICENSE](LICENSE)를 참조하십시오.
