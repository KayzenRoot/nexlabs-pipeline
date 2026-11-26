"""Offline private-network descriptor validation; no socket/configuration code."""
from __future__ import annotations

from dataclasses import dataclass
import ipaddress
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network

from .contracts import require, require_id, SecurityError

IPV4_PRIVATE = tuple(ipaddress.ip_network(value) for value in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8",
))
IPV6_PRIVATE = tuple(ipaddress.ip_network(value) for value in ("fc00::/7", "::1/128"))


@dataclass(frozen=True)
class NetworkPeer:
    peer_id: str
    address: str
    allowed_ips: tuple[str, ...]
    public_key_ref: str


@dataclass(frozen=True)
class ServiceBinding:
    service_id: str
    bind_address: str
    port: int
    exposure: str


@dataclass(frozen=True)
class NetworkPolicy:
    allowed_cidrs: tuple[str, ...] = ()
    peers: tuple[NetworkPeer, ...] = ()
    services: tuple[ServiceBinding, ...] = ()


def _within_private_range(value: IPv4Address | IPv6Address) -> bool:
    ranges = IPV4_PRIVATE if value.version == 4 else IPV6_PRIVATE
    return any(value in network for network in ranges)


def _private_ip(value: str) -> IPv4Address | IPv6Address:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise SecurityError("NETWORK_ADDRESS_INVALID") from exc
    require(not (address.is_unspecified or address.is_multicast or address.is_link_local),
            "NETWORK_ADDRESS_NOT_ROUTABLE_PRIVATE")
    require(_within_private_range(address), "PUBLIC_NETWORK_FORBIDDEN")
    return address


def _private_network(value: str) -> IPv4Network | IPv6Network:
    try:
        network = ipaddress.ip_network(value, strict=True)
    except ValueError as exc:
        raise SecurityError("NETWORK_CIDR_INVALID") from exc
    require(network.prefixlen != 0, "DEFAULT_ROUTE_FORBIDDEN")
    ranges = IPV4_PRIVATE if network.version == 4 else IPV6_PRIVATE
    require(any(network.subnet_of(allowed) for allowed in ranges),
            "PUBLIC_NETWORK_FORBIDDEN")
    return network


def validate_network_policy(policy: NetworkPolicy) -> None:
    require(isinstance(policy, NetworkPolicy), "NETWORK_POLICY_INVALID")
    networks = tuple(_private_network(item) for item in policy.allowed_cidrs)
    require(len(networks) == len(set(networks)), "NETWORK_CIDR_DUPLICATE")
    peer_ids: set[str] = set()
    key_refs: set[str] = set()
    for peer in policy.peers:
        require_id(peer.peer_id, "NETWORK_PEER_ID_INVALID")
        require_id(peer.public_key_ref, "NETWORK_KEY_REFERENCE_INVALID")
        require(peer.peer_id not in peer_ids, "NETWORK_PEER_DUPLICATE")
        require(peer.public_key_ref not in key_refs, "NETWORK_KEY_REFERENCE_DUPLICATE")
        peer_ids.add(peer.peer_id)
        key_refs.add(peer.public_key_ref)
        address = _private_ip(peer.address)
        require(any(address.version == net.version and address in net for net in networks),
                "NETWORK_PEER_OUTSIDE_ALLOWLIST")
        allowed = tuple(_private_network(item) for item in peer.allowed_ips)
        require(bool(allowed), "NETWORK_PEER_ALLOWLIST_EMPTY")
        require(len(allowed) == len(set(allowed)), "NETWORK_PEER_CIDR_DUPLICATE")
        for subnet in allowed:
            require(any(subnet.version == net.version and subnet.subnet_of(net)
                        for net in networks), "NETWORK_PEER_ROUTE_OUTSIDE_ALLOWLIST")
    service_ids: set[str] = set()
    for service in policy.services:
        require_id(service.service_id, "NETWORK_SERVICE_ID_INVALID")
        require(service.service_id not in service_ids, "NETWORK_SERVICE_DUPLICATE")
        service_ids.add(service.service_id)
        address = _private_ip(service.bind_address)
        require(type(service.port) is int and 1 <= service.port <= 65535,
                "NETWORK_PORT_INVALID")
        require(service.exposure in {"PRIVATE", "LOOPBACK"}, "NETWORK_SERVICE_EXPOSURE_DENY")
        if address.is_loopback:
            require(service.exposure == "LOOPBACK", "NETWORK_LOOPBACK_EXPOSURE_MISMATCH")
        else:
            require(service.exposure == "PRIVATE", "NETWORK_PRIVATE_EXPOSURE_MISMATCH")
            require(any(address.version == net.version and address in net for net in networks),
                    "NETWORK_SERVICE_OUTSIDE_ALLOWLIST")
