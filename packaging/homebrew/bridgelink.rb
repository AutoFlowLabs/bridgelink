# Homebrew Formula for BridgeLink
# Install: brew install AutoFlowLabs/tap/bridgelink
# Or: brew tap AutoFlowLabs/tap && brew install bridgelink

class Bridgelink < Formula
  include Language::Python::Virtualenv

  desc "CLI tool to expose Android devices remotely via NativeBridge"
  homepage "https://github.com/AutoFlowLabs/bridgelink"
  url "https://files.pythonhosted.org/packages/source/b/bridgelink/bridgelink-0.2.2.tar.gz"
  sha256 "PLACEHOLDER_SHA256"  # Update this after PyPI release
  license "MIT"
  head "https://github.com/AutoFlowLabs/bridgelink.git", branch: "production"

  depends_on "python@3.11"

  resource "click" do
    url "https://files.pythonhosted.org/packages/source/c/click/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/source/r/requests/requests-2.31.0.tar.gz"
    sha256 "942c5a758f98d790eaed1a29cb6eefc7ffb0d1cf7af05c3d2791656dbd6ad1e1"
  end

  resource "psutil" do
    url "https://files.pythonhosted.org/packages/source/p/psutil/psutil-5.9.8.tar.gz"
    sha256 "6be126e3225486dff286a8fb9a06246a5253f4c7c53b475ea5f5ac934e64194c"
  end

  resource "colorama" do
    url "https://files.pythonhosted.org/packages/source/c/colorama/colorama-0.4.6.tar.gz"
    sha256 "08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44"
  end

  resource "tabulate" do
    url "https://files.pythonhosted.org/packages/source/t/tabulate/tabulate-0.9.0.tar.gz"
    sha256 "0095b12bf5966de529c0feb1fa08671671b3368eec77d7ef7ab114be2c068b3c"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/source/c/charset-normalizer/charset-normalizer-3.3.2.tar.gz"
    sha256 "f30c3cb33b24454a82faecaf01b19c18562b1e89558fb6c56de4d9118a032fd5"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/source/i/idna/idna-3.6.tar.gz"
    sha256 "9ecdbbd083b06798ae1e86adcbfe8ab1479cf864e4ee30fe4e46a003d12491ca"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/source/u/urllib3/urllib3-2.1.0.tar.gz"
    sha256 "df7aa8afb0148fa78488e7899b2c59b5f4ffcfa82e6c54ccb9dd37c1d7b52d54"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/source/c/certifi/certifi-2024.8.30.tar.gz"
    sha256 "bec941d2aa8195e248a60b31ff9f0558284cf01a52591ceda73ea9afffd69fd9"
  end

  def install
    virtualenv_install_with_resources
  end

  def caveats
    <<~EOS
      BridgeLink has been installed!

      Quick Start:
        1. Run setup to install required tools (ADB, bore):
           bridgelink setup

        2. Set your API key:
           export NB_API_KEY='your-api-key'

        3. Add a device:
           bridgelink devices add <device-serial>

        4. Connect remotely:
           adb connect bridgelink.nativebridge.io:<port>

      Get your API key: https://nativebridge.io/dashboard/api-keys
      Documentation: https://github.com/AutoFlowLabs/bridgelink
    EOS
  end

  test do
    assert_match "BridgeLink", shell_output("#{bin}/bridgelink --version")
  end
end
