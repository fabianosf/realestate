# VPN WireGuard

Coloque seu arquivo de configuração WireGuard aqui com o nome `wg0.conf`.

O container `wireguard` montará esta pasta em `/config` e ativará o túnel automaticamente.
O serviço `celery_worker` usa `network_mode: "service:wireguard"`, ou seja, todo tráfego
de scraping passa pelo túnel VPN.

## Exemplo de wg0.conf

```ini
[Interface]
PrivateKey = SEU_PRIVATE_KEY
Address = 10.0.0.2/32
DNS = 1.1.1.1

[Peer]
PublicKey = PUBLIC_KEY_DO_SERVIDOR
Endpoint = servidor.vpn.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```
