from opinion_synthesizer import OpinionSynthesizer
from hippocampus.fact_router import FactRouter


def run_opinion_synthesizer_test():
    router = FactRouter()
    synthesizer = OpinionSynthesizer(router=router, max_facts=5)
    opinion = synthesizer.synthesize_opinion()
    assert "opinion" in opinion
    assert "confidence" in opinion
    print("[OpinionSynthesizerTest] Opinion synthesized:", opinion["opinion"])


if __name__ == "__main__":
    run_opinion_synthesizer_test()
