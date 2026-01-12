#!/usr/bin/env python3
"""
Script de vérification de MPS (Metal Performance Shaders) pour Mac Apple Silicon
Usage: python scripts/verify_mps.py
"""

import sys
import platform

def check_system():
    """Vérifie que nous sommes sur macOS Apple Silicon."""
    print("🔍 Vérification du système...")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    
    if platform.system() != "Darwin":
        print("❌ Ce script est conçu pour macOS uniquement")
        return False
    
    if platform.machine() != "arm64":
        print("⚠️  Vous n'êtes pas sur un Mac Apple Silicon (arm64)")
        print("   MPS nécessite un Mac avec processeur Apple Silicon (M1/M2/M3/M4)")
        return False
    
    print("✅ Système compatible")
    return True

def check_pytorch():
    """Vérifie que PyTorch est installé."""
    print("\n🔍 Vérification de PyTorch...")
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} installé")
        return torch
    except ImportError:
        print("❌ PyTorch n'est pas installé")
        print("   💡 Installez-le avec: pip install torch torchvision torchaudio")
        return None

def check_mps(torch):
    """Vérifie que MPS est disponible et fonctionne."""
    print("\n🔍 Vérification de MPS (Metal Performance Shaders)...")
    
    if not hasattr(torch.backends, 'mps'):
        print("❌ MPS n'est pas disponible dans cette version de PyTorch")
        print("   💡 Assurez-vous d'avoir PyTorch 2.0+ avec support MPS")
        return False
    
    if not torch.backends.mps.is_available():
        print("❌ MPS n'est pas disponible sur ce système")
        print("   💡 Vérifiez que vous êtes sur un Mac Apple Silicon")
        print("   💡 Vérifiez que macOS est à jour")
        return False
    
    print("✅ MPS est disponible")
    
    # Test de fonctionnement
    print("\n🧪 Test de fonctionnement MPS...")
    try:
        device = torch.device("mps")
        print(f"   Device: {device}")
        
        # Test simple
        x = torch.ones(1, device=device)
        print(f"   ✅ Tenseur créé sur MPS: {x}")
        
        # Test de calcul
        a = torch.randn(1000, 1000, device=device)
        b = torch.randn(1000, 1000, device=device)
        c = torch.mm(a, b)
        print(f"   ✅ Calcul matriciel réussi sur MPS")
        print(f"   ✅ MPS fonctionne correctement!")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur lors du test MPS: {e}")
        print("   💡 MPS est disponible mais rencontre des problèmes")
        return False

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🚀 Vérification de la configuration MPS pour Mac Apple Silicon")
    print("=" * 70)
    print()
    
    # Vérifier le système
    if not check_system():
        sys.exit(1)
    
    # Vérifier PyTorch
    torch = check_pytorch()
    if torch is None:
        sys.exit(1)
    
    # Vérifier MPS
    mps_available = check_mps(torch)
    
    print("\n" + "=" * 70)
    if mps_available:
        print("✅ Configuration MPS complète et fonctionnelle!")
        print("   🚀 Vous pouvez utiliser le GPU pour l'entraînement")
    else:
        print("⚠️  MPS n'est pas disponible")
        print("   💡 L'entraînement utilisera le CPU (plus lent)")
    print("=" * 70)
    
    return 0 if mps_available else 1

if __name__ == "__main__":
    sys.exit(main())

