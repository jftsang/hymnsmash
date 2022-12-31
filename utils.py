class BinomialDistribution:
    @staticmethod
    def estimate_p(n, ns, z=1.96) -> (float, float):
        """Wilson score interval estimator
        https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Wilson_score_interval
        """
        nf = n - ns
        phat = (ns + z ** 2 / 2) / (n + z ** 2)
        error = z / (n + (z ** 2)) * (ns * nf / n + (z ** 2) / 4) ** 0.5
        return phat, error
